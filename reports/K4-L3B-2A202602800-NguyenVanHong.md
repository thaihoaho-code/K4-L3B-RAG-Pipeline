# Individual Contribution Report

## Thông tin

- **Họ và tên:** Nguyễn Văn Hồng
- **Mã học viên:** 2A202602800
- **Nhóm:** LemonThree
- **Repository:** https://github.com/thaihoaho-code/K4-L3B-RAG-Pipeline-LemonThree

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| **Task 1 — Legal corpus collection** | Thu thập tối thiểu 3 văn bản pháp lý chính thức liên quan đến xử lý hóa đơn điện tử có sai sót và đưa vào corpus pháp lý của nhóm. Kiểm tra nguồn và phạm vi nội dung trước khi sử dụng cho pipeline RAG. | `data/landing/legal/` | Done |
| **Task 2 — Public article crawling** | Hoàn thiện danh sách nguồn public và logic crawl bài viết; chuẩn hóa dữ liệu mỗi bài về các trường `url`, `title`, `date_crawled`, `content_markdown`. Xử lý trường hợp một nguồn bị Cloudflare chặn bằng cách thay bằng nguồn công khai khác có thể crawl ổn định. | `src/task2_crawl_news.py`, `data/landing/news/` | Done |
| **Task 6 — BM25 lexical retrieval** | Triển khai lexical retrieval bằng BM25 trên cùng tập chunks của pipeline; hỗ trợ tìm kiếm dựa trên token/từ khóa và trả kết quả theo contract chung của hệ thống. | task6_lexical_search.py / BM25 retrieval trong `src/` | Done |
| **Task 9 — Retrieval pipeline** | Tham gia hoàn thiện retrieval pipeline kết hợp dense retrieval và BM25, fuse kết quả bằng RRF; áp dụng threshold trên dense score và sử dụng PageIndex/vectorless fallback khi confidence retrieval thấp. Giữ hybrid result làm fallback nếu PageIndex gặp lỗi. | `src/task9_retrieval_pipeline.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Kết hợp dense retrieval và BM25 thay vì chỉ sử dụng một phương pháp retrieval.  
   **Lý do/evidence:** Corpus pháp lý chứa cả câu hỏi cần khớp chính xác thuật ngữ, số hiệu hoặc cụm từ pháp lý và các câu hỏi diễn đạt lại theo ngữ nghĩa. BM25 hỗ trợ tốt exact/lexical matching, trong khi dense retrieval bổ sung khả năng semantic matching.  
   **Trade-off:** Pipeline phức tạp hơn và cần bước fusion để tránh hai retriever trả kết quả trùng hoặc xếp hạng không đồng nhất.

2. **Quyết định:** Chỉ kích hoạt PageIndex fallback khi dense retrieval không vượt ngưỡng đủ tin cậy thay vì gọi fallback cho mọi query.  
   **Lý do/evidence:** Giúp giữ retrieval path chính đơn giản và giảm chi phí xử lý không cần thiết; fallback chỉ được sử dụng trong các trường hợp retrieval thông thường yếu.  
   **Trade-off:** Chất lượng phụ thuộc vào việc hiệu chỉnh threshold; threshold quá cao có thể kích hoạt fallback quá nhiều, còn quá thấp có thể bỏ sót các query khó.

## Kiểm thử và kết quả

- **Test hoặc query tôi đã dùng:**
  - Chạy acceptance test cho phần corpus/crawl sau khi chuẩn hóa dữ liệu.
  - Chạy contract test cho retrieval:
    ```bash
    pytest tests/test_contracts.py -q
    ```
  - Kiểm tra các query retrieval với BM25 và retrieval pipeline để đảm bảo kết quả trả về đúng contract và đúng `retrieval_method`.

- **Kết quả trước/sau nếu có:**
  - Phần thu thập/crawl corpus đã đạt các test acceptance liên quan.
  - Sau khi hoàn thiện Task 6, bộ contract test đạt **15/15 tests pass**.
  - Retrieval pipeline được thiết kế để ưu tiên hybrid Dense + BM25 + RRF và chỉ chuyển sang fallback khi score không đạt threshold.

- **Lỗi đã phát hiện và cách xử lý:**
  - Một nguồn crawl public gặp lỗi do Cloudflare; thay bằng nguồn công khai khác có nội dung phù hợp và có thể thu thập ổn định.
  - Quá trình cài Chromium cho Playwright từng gặp lỗi kết nối `ECONNRESET`; sau khi cài lại, kiểm tra launch Playwright thành công.
  - Khi làm việc với dữ liệu crawl, `git pull` từng bị chặn do các file JSON local chưa được track trùng với file từ remote; xử lý bằng cách bảo toàn dữ liệu local và đồng bộ đúng path cần thiết thay vì ghi đè trực tiếp.

## Điều còn hạn chế

- **Một hạn chế cụ thể của phần tôi làm:** Retrieval pipeline vẫn phụ thuộc vào việc lựa chọn threshold và chất lượng corpus/chunking đầu vào. Với một số query có cách diễn đạt quá khác corpus hoặc evidence nằm rải rác ở nhiều đoạn, cả lexical và dense retrieval vẫn có thể xếp hạng chưa tối ưu.

- **Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện:** Chạy thêm một tập benchmark có nhãn relevance để hiệu chỉnh threshold và trọng số/fusion giữa Dense và BM25, sau đó phân tích riêng các failure case của PageIndex fallback để xác định trường hợp nào thực sự cần kích hoạt fallback.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 25/09/2026
- **Tên thành viên:** Nguyễn Văn Hồng