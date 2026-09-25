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
Mặc dù Config A tốt nhất, hệ thống vẫn chưa đạt điểm tuyệt đối về khả năng truy xuất Context:
1. **Lỗi nhiễu Chunking:** Một số câu hỏi truy xuất ra những đoạn văn bản bị cắt giữa chừng (cắt ngang ý), dẫn đến Recall chưa đạt 1.0. 
2. **Từ khóa trùng lặp:** Những câu hỏi về xử lý sai sót hóa đơn thường lấy ra cả quy định chung lẫn quy định riêng biệt do độ tương đồng ngữ nghĩa (Cosine Similarity) của chúng là quá sát nhau.

## 5. Recommendations
Dựa trên kết quả thực tế, nhóm đề xuất hướng cải thiện:
- **Tối ưu hóa tham số RRF:** Thay vì để RRF với công thức `1 / (rank + 60)` chia đều trọng số 50-50 cho cả Dense và BM25, cần tinh chỉnh lại trọng số (Weighted Hybrid Search). Có thể cấp cho Dense 80% trọng số và BM25 chỉ chiếm 20% (chỉ dùng BM25 để rà sót mã số luật).
- **Cải thiện thuật toán Chunking:** Áp dụng phương pháp `Parent Document Retriever` hoặc Semantic Chunking thay vì chia cắt cố định (RecursiveCharacterTextSplitter) để bảo toàn trọn vẹn ngữ nghĩa các điều luật.
- **Tùy chỉnh hệ số phạt BM25:** Loại bỏ triệt để các Stop words tiếng Việt chuyên ngành thuế để BM25 không bị nhiễu.
