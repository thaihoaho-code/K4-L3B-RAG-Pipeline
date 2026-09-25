# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-25 |
| Framework and version              | Ragas 0.4.3 |
| Evaluator model                    | gemini-3.6-flash |
| Generator model                    | gemini-3.6-flash |
| Embedding model                    | gemini-embedding-001 |
| Corpus version/commit              | Nghị định 254, Thông tư 91 và 5 bài báo |
| Golden dataset size                | 15 Q&A |
| `top_k`                            | 5 |
| Fallback threshold and calibration | 0.3 |

## Configurations

- **Config A — dense-only:** Chỉ sử dụng Semantic Search (ChromaDB).
- **Config B — hybrid + RRF:** Kết hợp Dense Search + Lexical (BM25) và gộp điểm bằng RRF.

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |     1.00 |     0.96 |     -0.04 |
| Answer relevance  |      N/A |      N/A |         0 |
| Context recall    |     0.77 |     0.60 |     -0.17 |
| Context precision |     0.78 |     0.74 |     -0.04 |
| **Average**       |     0.85 |     0.76 |     -0.09 |

## A/B comparison

- Cấu hình tốt hơn: Config A
- Evidence: Điểm số truy xuất (Context Recall và Precision) của Config A cao hơn hẳn Config B. Config A bảo toàn được tỷ lệ "Faithfulness" tuyệt đối (1.00). RRF trong Config B vô tình đẩy nhiễu từ BM25 lên top đầu.
- Trade-off về latency/cost: Config A chạy nhanh hơn do không phải mất thêm thời gian tokenize và tính toán điểm BM25. Cả hai config đều tốn cost như nhau cho việc embed câu hỏi và sinh text.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Nếu hóa đơn khởi tạo từ máy tính tiền bị sai tên, địa chỉ thì có được miễn lập lại hóa đơn không? | B | 0.90 | N/A | 0.50 | 0.40 | retrieval | Dense và BM25 lấy nhầm quy định chung lên top đầu, đẩy quy định máy tính tiền xuống dưới. |
|   2 | Các đối tượng nào không được tính là người bán phải lập hóa đơn điện tử theo NĐ 254? | A | 1.00 | N/A | 0.33 | 0.60 | retrieval | Mô hình Dense bỏ qua từ "không" mang nghĩa phủ định và truy xuất các điều luật đối tượng áp dụng. |
|   3 | Nếu trong cùng 1 tháng tôi lập sai nhiều hóa đơn của cùng 1 người mua thì có được gom chung lại xử lý không? | A | 1.00 | N/A | 0.45 | 0.55 | data | Lỗi nhiễu Chunking. Thuật toán cắt theo độ dài vô tình cắt ngang ý nghĩa quy định lập bảng kê. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Áp dụng Semantic Chunking | Case 3 bị thiếu hụt Context Recall do luật bị ngắt đôi giữa 2 chunk. | Không còn tình trạng lấy được nửa đầu điều luật nhưng mất đoạn bổ sung đằng sau. | Xóa DB cũ, chạy lại index, đo lại Recall Case 3 vượt 0.85. |
|        2 | Thêm Query Rewriting | Case 2 hệ thống không hiểu câu hỏi phủ định, bỏ sót từ "không". | LLM sẽ biên dịch lại query thành dạng khẳng định, lọc từ khoá trước khi retrieve. | So sánh Context Precision luồng có/không Query Rewriting. |
|        3 | Dùng Weighted Hybrid thay cho RRF | RRF làm Case 1 bị đẩy các chunk rác của BM25 lên Top 5. | Cấp 80% trọng số cho Dense và 20% cho BM25 sẽ giảm nhiễu mà vẫn bắt được mã luật. | Chạy lại Config B với RRF có trọng số tùy chỉnh để xem Delta. |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Không thực hiện | N/A | N/A | N/A | N/A |
