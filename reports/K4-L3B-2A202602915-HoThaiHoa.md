# Individual contribution report

---

## Thông tin

- Họ và tên: Hồ Thái Hòa
- Mã học viên: 2A202602915
- Nhóm: LemonThree
- Repository/branch: main

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 4: Chunking & Indexing | Đọc Markdown, chặt nhỏ (RecursiveChunking), gọi API nhúng và upsert vào ChromaDB. Sửa lỗi tương thích kiểu dữ liệu `ContentEmbedding` của Gemini. | `src/task4_chunking_indexing.py` | Done |
| Task 5: Semantic Search | Viết hàm truy vấn trực tiếp vào collection của ChromaDB bằng Cosine Distance để trả về `SearchResult`. | `src/task5_semantic_search.py` | Done |
| Task 8: PageIndex Fallback | Tích hợp thư viện `fpdf2` để xuất Markdown thành file PDF ảo, sau đó đẩy lên API PageIndex để làm luồng Retrieval dự phòng (Vectorless). | `src/task8_pageindex_vectorless.py` | Done |

## Quyết định kỹ thuật quan trọng

Mô tả tối đa hai quyết định mà bạn trực tiếp tham gia:

1. **Quyết định:** Sử dụng `RecursiveCharacterTextSplitter` với Chunk Size 500, Overlap 50 và chọn Model `gemini-embedding-001` cho Vector Database.
   **Lý do/evidence:** Văn bản luật thuế thường có cấu trúc điều/khoản/điểm khá dài. Nếu cắt quá ngắn (100-200) sẽ làm đứt mạch ngữ nghĩa. Cắt ở ngưỡng 500 giúp bao trọn 1-2 khoản luật trọng tâm. Dùng Gemini để đồng bộ hệ sinh thái với LLM Generator.
   **Trade-off:** Chunk to giúp giữ ngữ cảnh tốt nhưng cũng có nguy cơ kéo theo thông tin nhiễu khi query. Phụ thuộc hoàn toàn vào API Gemini (cần kết nối mạng) thay vì tự host model Local.

2. **Quyết định:** Viết logic tự động xuất file (render) văn bản Markdown thành file PDF thông qua thư viện `fpdf` ngay trong lúc chạy pipeline (Task 8).
   **Lý do/evidence:** SDK/API của công cụ PageIndex không hỗ trợ nhét thô chuỗi Text/Markdown trực tiếp, bắt buộc phải truyền vào đường dẫn file `.pdf` hợp lệ để nó trích xuất số trang (page index).
   **Trade-off:** Thêm thư viện trung gian làm tăng nhẹ thời gian thực thi (latency) và các thành phần phức tạp trong Markdown (như bảng biểu, link) có thể bị hiển thị không đẹp bằng định dạng gốc.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: Chạy bộ test `pytest tests/test_contracts.py` (cụ thể là `test_semantic_search_returns_contract` và `test_pageindex_returns_contract`) để kiểm chứng cấu trúc Output đúng định dạng JSON.
- Kết quả trước/sau nếu có: Pipeline chạy xuyên suốt từ khâu nhúng dữ liệu đến khâu trích xuất thành công.
- Lỗi đã phát hiện và cách xử lý: Lỗi Crash `ValueError` ở ChromaDB do Gemini API trả về mảng Object `ContentEmbedding` thay vì mảng số. Đã xử lý bằng cách dùng List Comprehension móc trường `.values` ra trước khi upsert vào DB (`[emb.values for emb in response.embeddings]`).

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Hàm `task4` hiện đang đẩy thô (re-embed) toàn bộ nội dung Markdown lên Gemini API mỗi khi chạy lại script. Quá trình này không có cơ chế chặn trùng lặp, gây tốn thời gian chờ và lãng phí Quota API.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Bổ sung thuật toán tạo băm (Hash MD5) cho từng đoạn Chunk. Check Hash trong Metadata của ChromaDB, nếu Chunk chưa từng thay đổi thì bỏ qua bước gọi API Embedding.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-25
- Tên thành viên: Hồ Thái Hòa
