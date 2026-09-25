# Báo cáo đóng góp cá nhân — Nguyễn Việt Hoàng

## Thông tin

- Họ và tên: Nguyễn Việt Hoàng
- Mã học viên: 02424
- Vai trò: Thành viên
- Nhóm: LemonThree
- Repository: https://github.com/thaihoaho-code/K4-L3B-RAG-Pipeline-LemonThree
- Nhánh làm việc: `main`
- Ngày báo cáo: 25/09/2026

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/test đối chiếu | Trạng thái |
|---|---|---|---|
| Task 3 — Chuẩn hóa corpus | Chuyển tài liệu pháp lý và bài viết sang Markdown, giữ cấu trúc `standardized/legal` và `standardized/news`, bổ sung metadata và nội dung có thể truy xuất. | `src/task3_convert_markdown.py`, `data/standardized/`, commit `4ad1534` | Done |
| Task 7 — RRF | Gộp danh sách dense và BM25 theo Reciprocal Rank Fusion, cộng điểm theo thứ hạng, loại trùng ID và trả kết quả với `retrieval_method="hybrid"`. | `src/task7_reranking.py`, `tests/test_contracts.py::test_rrf_uses_rank_deduplicates_and_marks_hybrid`, commit nhóm `7a6a56c` | Done |
| Task 10 — Generation có citation | Nhận kết quả retrieval, sắp xếp lại context, định dạng title/source để tạo citation, gọi LLM provider và trả safe refusal khi không có bằng chứng. | `src/task10_generation.py`, `tests/test_contracts.py::test_reorder_is_non_mutating_and_context_contains_source`, `test_generation_result_validator_accepts_safe_refusal`, commit nhóm `fbc4942` | Done |

## Quyết định kỹ thuật quan trọng

1. **Giữ metadata và nguồn truy nguyên khi chuẩn hóa corpus.**
   **Lý do/evidence:** `task3_convert_markdown.py` giữ riêng `standardized/legal` và `standardized/news`, đồng thời ghi title, source file, URL và thời điểm chuyển đổi trong frontmatter.
   **Trade-off:** Markdown có thêm metadata và kích thước lớn hơn, nhưng có thể đối chiếu chunk với tài liệu gốc khi debug hoặc trích dẫn.

2. **Dùng RRF để hợp nhất dense và BM25 theo thứ hạng.**
   **Lý do/evidence:** `task7_reranking.py` dùng công thức `1 / (k + rank)`, bắt đầu rank từ 1, loại kết quả trùng ID và gắn `retrieval_method="hybrid"`.
   **Trade-off:** Không cần ép cosine score và BM25 score về cùng một thang đo, nhưng RRF chỉ phản ánh thứ hạng và không giữ nguyên ý nghĩa điểm similarity gốc.

## Kiểm thử và kết quả

- Acceptance test: `.venv\Scripts\python.exe -m pytest tests/test_acceptance.py -q` — **5 passed**.
- RRF contract test: `pytest tests/test_contracts.py -q -k test_rrf_uses_rank_deduplicates_and_marks_hybrid` — **passed**.
- Generation contract tests: kiểm tra reorder không làm thay đổi dữ liệu gốc, context có source/title và safe refusal đúng schema — **passed** khi provider được cấu hình.
- Toàn bộ test với biến môi trường embedding được cấu hình: **20 passed**.
- Lỗi đã phát hiện: nếu thiếu cấu hình embedding hoặc LLM provider, các module generation/retrieval có thể dừng ngay khi import hoặc khi gọi provider. Không ghi API key vào repository.

## Điều còn hạn chế

- Commit triển khai RRF và Generation hiện nằm trong lịch sử commit chung của nhóm; chưa có branch hoặc pull request riêng mang tên cá nhân.
- Cần tách khởi tạo provider khỏi thời điểm import module và bổ sung test mock cho LLM để generation có thể kiểm thử mà không cần API key thật.
- Phần A/B evaluation là artifact chung của nhóm; cần tiếp tục kiểm chứng các câu hỏi golden với nguồn pháp lý trước khi kết luận chất lượng retrieval.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Nguyễn Việt Hoàng
