# Báo cáo đóng góp cá nhân — Nguyễn Việt Hoàng

## Thông tin

- Họ và tên: Nguyễn Việt Hoàng
- Mã học viên: 02424
- Vai trò: Thành viên
- Nhóm: 
- Repository: https://github.com/thaihoaho-code/K4-L3B-RAG-Pipeline
- Nhánh làm việc: `main`
- Ngày báo cáo: 25/09/2026

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/test đối chiếu | Trạng thái |
|---|---|---|---|
| Task 3 — Chuẩn hóa corpus | Chuyển tài liệu pháp lý và bài viết sang Markdown, giữ cấu trúc `standardized/legal` và `standardized/news`, bổ sung metadata và nội dung có thể truy xuất. | `src/task3_convert_markdown.py`, `data/standardized/`, commit `4ad1534` | Done |
| Task 5 — Semantic Search | Dùng lại `embed_texts()` của Task 4 để embed query, truy vấn ChromaDB, đổi cosine distance thành similarity, trả `SearchResult` với `retrieval_method="dense"`, sắp xếp giảm dần và giới hạn `top_k`. | `src/task5_semantic_search.py`, `tests/test_contracts.py::test_semantic_search_uses_shared_embedding_and_contract` | Done |
| Task 7 — RRF | Gộp danh sách dense và BM25 theo Reciprocal Rank Fusion, cộng điểm theo thứ hạng, loại trùng ID và trả kết quả với `retrieval_method="hybrid"`. | `src/task7_reranking.py`, `tests/test_contracts.py::test_rrf_uses_rank_deduplicates_and_marks_hybrid`, commit nhóm `7a6a56c` | Done |

## Quyết định kỹ thuật quan trọng

1. **Dùng chung hàm embedding giữa corpus và query.**
   **Lý do/evidence:** `task5_semantic_search.py` import và gọi `embed_texts([query])` từ Task 4; contract test kiểm tra query embedding được truyền vào ChromaDB.
   **Trade-off:** Giữ đúng model và dimension giữa index/query, nhưng việc import provider embedding yêu cầu biến môi trường API khi chạy test hoặc pipeline thật.

2. **Dùng RRF để hợp nhất dense và BM25 theo thứ hạng.**
   **Lý do/evidence:** `task7_reranking.py` dùng công thức `1 / (k + rank)`, bắt đầu rank từ 1, loại kết quả trùng ID và gắn `retrieval_method="hybrid"`.
   **Trade-off:** Không cần ép cosine score và BM25 score về cùng một thang đo, nhưng RRF chỉ phản ánh thứ hạng và không giữ nguyên ý nghĩa điểm similarity gốc.

## Kiểm thử và kết quả

- Acceptance test: `.venv\Scripts\python.exe -m pytest tests/test_acceptance.py -q` — **5 passed**.
- Semantic Search contract test với provider được cấu hình bằng biến môi trường: `pytest tests/test_contracts.py -q -k semantic_search_uses_shared_embedding_and_contract` — **1 passed, 14 deselected**.
- RRF contract test: `pytest tests/test_contracts.py -q -k test_rrf_uses_rank_deduplicates_and_marks_hybrid` — **passed**.
- Toàn bộ test với biến môi trường embedding được cấu hình: **20 passed**.
- Lỗi đã phát hiện: nếu thiếu `GEMINI_API_KEY`/cấu hình embedding, `genai.Client()` được khởi tạo ngay khi import Task 4 và contract test dừng trước khi chạy logic search. Không ghi API key vào repository.

## Điều còn hạn chế

- Commit triển khai Semantic Search và RRF hiện nằm trong lịch sử commit chung của nhóm; chưa có branch hoặc pull request riêng mang tên cá nhân.
- Cần tách khởi tạo embedding client khỏi thời điểm import module để test contract có thể chạy mà không cần API key thật.
- Phần A/B evaluation là artifact chung của nhóm; cần tiếp tục kiểm chứng các câu hỏi golden với nguồn pháp lý trước khi kết luận chất lượng retrieval.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Nguyễn Việt Hoàng
