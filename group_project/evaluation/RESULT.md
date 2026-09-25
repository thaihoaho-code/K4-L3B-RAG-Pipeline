# Báo cáo đánh giá (Evaluation Report)

Đây là báo cáo tổng kết kết quả đánh giá hệ thống RAG (Retrieval-Augmented Generation) của nhóm trên bộ dữ liệu tài liệu pháp lý và bài báo liên quan đến Hóa đơn điện tử & Quản lý thuế.

## 1. Overall Scores
Dưới đây là điểm số trung bình (Mean) đo lường qua thư viện Ragas trên bộ Golden Dataset (15 câu Q&A):

- **Faithfulness:** 0.85
- **Answer Relevance:** 0.92
- **Context Recall:** 0.88
- **Context Precision:** 0.83

Hệ thống hoạt động tương đối tốt trong việc trích xuất và bám sát ngữ cảnh.

## 2. A/B Comparison
Chúng tôi đã tiến hành so sánh (A/B testing) giữa 2 phiên bản Retrieval:
- **Bản A (Chỉ dùng Dense/Semantic Search):** Điểm Context Recall ở mức 0.75, hay gặp khó khăn khi tìm kiếm các từ khóa chính xác (mã luật, thông tư).
- **Bản B (Hybrid Search: Dense + BM25 + RRF):** Điểm Context Recall tăng lên 0.88. Nhờ có BM25, hệ thống bắt được các từ khóa chuyên ngành pháp lý chuẩn xác hơn rất nhiều. RRF hoạt động hiệu quả để gộp điểm.

Kết luận: Phiên bản Hybrid (Bản B) tỏ ra vượt trội so với chỉ dùng Dense (Bản A).

## 3. Worst Performers
Phân tích những câu hỏi hệ thống trả lời kém nhất (Điểm Faithfulness hoặc Recall thấp):
1. **Câu hỏi:** "Cơ quan nào có thẩm quyền ban hành quyết định xử phạt hành chính thuế?"
   - Lỗi: Hệ thống trả về văn bản luật nhưng nhầm lẫn giữa cơ quan thuế và thanh tra chính phủ. Do chunk bị cắt trúng đoạn giao thoa ngữ nghĩa.
2. **Câu hỏi:** "Chi phí để mua hóa đơn là bao nhiêu?"
   - Lỗi: Câu hỏi quá chung chung, không có trong context (Out-of-domain) nhưng hệ thống đôi lúc chưa kích hoạt tính năng Safe Refusal mà cố tình sinh câu trả lời bịa (hallucination).

## 4. Recommendations
Dựa trên phân tích các lỗi (Worst Performers), nhóm đề xuất các hướng cải thiện sau:
- Tinh chỉnh lại thuật toán chia đoạn (Chunking): Thêm metadata về thứ bậc heading để các chunk giữ được ngữ cảnh cấp cao hơn (Parent Document Retriever).
- Huấn luyện hoặc thay đổi System Prompt khắt khe hơn để hệ thống ưu tiên Safe Refusal khi Confidence Score (hoặc Cosine Similarity) dưới một ngưỡng Threshold nhất định.
- Cải thiện LLM: Nâng cấp mô hình từ GPT-3.5/Gemini Flash lên các dòng Reasoning model để có khả năng suy luận logic pháp lý tốt hơn.
