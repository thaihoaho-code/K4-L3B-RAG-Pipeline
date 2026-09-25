# Báo cáo đánh giá (Evaluation Report)

Báo cáo tổng kết kết quả đánh giá hệ thống RAG trên bộ Golden Dataset (15 câu hỏi) liên quan đến Hóa đơn điện tử & Quản lý thuế.

## 1. Cấu hình kiểm thử (Test Configuration)
Để đánh giá chính xác tác động của thuật toán Reciprocal Rank Fusion (RRF), chúng tôi sử dụng phương pháp A/B Testing với nguyên tắc kiểm soát chặt chẽ các biến số. Trừ cấu hình Retrieval Strategy, **tất cả các yếu tố khác đều được giữ nguyên tuyệt đối**.

- **Ngày chạy:** 2026-09-25
- **Mô hình Generation (Model):** gemini-3.6-flash
- **Corpus Commit:** Dữ liệu chuẩn hóa gồm Nghị định 254, Thông tư 91 và 5 bài báo
- **Top_K:** 5
- **Score Threshold:** 0.3
- **Golden Dataset:** 15 câu Q&A (Lấy từ ngữ cảnh thực tế)
- **Evaluator:** RAGAS framework
- **System Prompt:** Không đổi

## 2. A/B Comparison
Hai cấu hình được đem ra so sánh:
- **Config A (Dense-only):** Chỉ sử dụng Semantic Search.
- **Config B (Hybrid + RRF):** Kết hợp Dense Search + Lexical (BM25) và gộp điểm bằng RRF.

| Metric | Config A (Dense-only) | Config B (Hybrid + RRF) | Chênh lệch (Delta) |
|---|---|---|---|
| **Faithfulness** | 1.00 | 0.96 | -0.04 |
| **Answer Relevance** | N/A* | N/A* | 0 |
| **Context Recall** | 0.77 | 0.60 | -0.17 |
| **Context Precision** | 0.78 | 0.74 | -0.04 |

*(**Ghi chú:** Chỉ số Answer Relevance bị NaN do thư viện Ragas Parser gặp lỗi tương thích với output markdown của Gemini API khi sinh câu hỏi ảo, hệ thống tạm thời ghi nhận là N/A).*

**Nhận xét A/B:** 
Kết quả thực tế gây bất ngờ lớn: **Config A (Dense-only) áp đảo hoàn toàn Config B (Hybrid + RRF)**. 
Trái với kỳ vọng ban đầu, việc đưa thêm thuật toán BM25 và RRF vào không làm kết quả tốt lên mà lại kéo tụt nghiêm trọng `Context Recall` (-0.17). Nguyên nhân được phân tích là do:
1. **Gemini Embedding quá tốt:** Semantic search của mô hình Embedding đã làm rất xuất sắc việc phân loại ngữ nghĩa văn bản pháp lý. Nó lấy được chính xác các đoạn thông tin cần thiết.
2. **Nhiễu từ BM25:** Lexical search (BM25) hoạt động bằng cách đếm từ khóa. Do văn bản pháp luật chứa lượng lớn các từ khóa lặp lại liên tục ở mọi chỗ (như "hóa đơn", "điện tử", "cơ quan thuế", "người bán"), BM25 chấm điểm cao cho rất nhiều đoạn văn (chunk) rác không chứa ý chính.
3. **RRF phản tác dụng:** Khi dùng RRF để cộng điểm, những chunk rác từ BM25 vô tình được đẩy lên top, làm "văng" mất các chunk chất lượng của Dense Search ra khỏi `Top 5`. Điều này khiến LLM không có đủ context chuẩn (Precision giảm xuống 0.74) và kéo theo Faithfulness cũng bị sứt mẻ một chút (xuống 0.96).

## 3. Overall Scores
Dựa trên kết quả đo lường, cấu hình chiến thắng cuối cùng là **Config A (Dense-only)**.
- Đạt điểm tuyệt đối ở **Faithfulness (1.00)**: 100% câu trả lời của LLM bám sát vào Context được cung cấp, hoàn toàn không bị ảo giác (hallucination).
- Context Precision và Context Recall ở mức ổn định (~0.77).

## 4. Worst Performers
Dưới đây là 3 trường hợp có điểm số truy xuất Context Recall và Precision kém nhất trong tập Golden Dataset và nguyên nhân gốc rễ:

1. **Trường hợp 1:** *"Nếu hóa đơn khởi tạo từ máy tính tiền bị sai tên, địa chỉ thì có được miễn lập lại hóa đơn không?"*
   - **Metric:** Context Precision thấp.
   - **Nguyên nhân gốc rễ:** Câu hỏi này có hai lớp ngữ nghĩa: "sai tên, địa chỉ" thường được miễn lập lại và "từ máy tính tiền" là ngoại lệ bắt buộc phải lập lại. Mô hình Dense Embedding bị bối rối và lấy nhầm các chunk quy định chung về hóa đơn thông thường lên top đầu, đẩy phần ngoại lệ về máy tính tiền xuống dưới.

2. **Trường hợp 2:** *"Các đối tượng nào không được tính là người bán phải lập hóa đơn điện tử theo NĐ 254?"*
   - **Metric:** Context Recall thấp.
   - **Nguyên nhân gốc rễ:** Câu hỏi mang tính chất phủ định logic. Các mô hình Embedding thường bỏ qua từ "không" và mapping thẳng câu hỏi này vào các đoạn văn bản mô tả về đối tượng áp dụng, khiến LLM không tìm thấy thông tin ngoại trừ.

3. **Trường hợp 3:** *"Nếu trong cùng 1 tháng tôi lập sai nhiều hóa đơn của cùng 1 người mua thì có được gom chung lại xử lý không?"*
   - **Metric:** Context Recall bị thiếu hụt.
   - **Nguyên nhân gốc rễ:** Lỗi nhiễu Chunking. Quy định về việc lập chung 1 bảng kê nằm ở cuối khoản 1, nhưng do thuật toán RecursiveCharacterTextSplitter cắt theo độ dài cố định, đoạn này bị tách sang một chunk khác biệt hoàn toàn với chunk nói về xử lý hóa đơn sai. 

## 5. Recommendations
Dựa trên các nguyên nhân gốc rễ trên, nhóm đề xuất phương án cải thiện và cách kiểm tra lại:

1. **Cải thiện thuật toán Chunking để xử lý trường hợp 3:**
   - **Đề xuất:** Áp dụng phương pháp Semantic Chunking hoặc Parent Document Retriever để không cắt ngang các điều khoản luật liên kết với nhau.
   - **Cách kiểm tra lại:** Xóa DB cũ, chạy lại index với thuật toán mới, sau đó chạy lại script đánh giá. Nếu Context Recall của trường hợp 3 tăng lên 1.0 hoặc Overall Recall vượt ngưỡng 0.85 thì phương án này thành công.

2. **Áp dụng Query Rewriting / HyDE để xử lý trường hợp 1 và 2:**
   - **Đề xuất:** Thêm một prompt phụ cho LLM để phân tích cú pháp (thấy từ "không" thì đổi thành search term phủ định) và phân rã ý (tách "máy tính tiền" thành keyword bắt buộc).
   - **Cách kiểm tra lại:** Cập nhật hàm retrieval để in ra query đã được rewrite, kiểm tra bằng mắt thường. Sau đó chạy A/B Test so sánh điểm Context Precision giữa luồng có Query Rewriting và không Query Rewriting trên chính Golden Dataset này để đo đếm mức độ chênh lệch.
