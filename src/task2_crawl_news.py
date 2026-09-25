"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
    
-> Dùng Firecrawl or bất cứ công cụ nào bạn quen    
"""

import asyncio
import json
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://thuvienphapluat.vn/phap-luat-doanh-nghiep/cong-viec-phap-ly/xu-ly-hoa-don-dien-tu-sai-sot-tu-ngay-01-7-2026-376.html",

    "https://www.meinvoice.vn/tin-tuc/13508/xu-ly-hoa-don-dien-tu-co-sai-sot/",

    "https://chinhsachonline.chinhphu.vn/hoa-don-tu-may-tinh-tien-sai-ten-dia-chi-co-phai-lap-lai-90814.htm",

    "https://chinhsachonline.chinhphu.vn/cach-xu-ly-hoa-don-dien-tu-tu-may-tinh-tien-bi-lap-sai-91567.htm",

    "https://cads.com.vn/vi/thong-tu-912026tt-btc-6-truong-hop-hoa-don-sai-sot-thuong-gap-va-cach-xu-ly-chi-tiet-nws311.html",
]


async def crawl_article(url: str) -> dict:
    """Crawl một bài viết và chuẩn hóa metadata."""

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)

        if not result.success:
            raise RuntimeError(
                f"Crawl failed: {url}"
            )

        title = "Unknown"

        if result.metadata:
            title = result.metadata.get("title", "Unknown")

        markdown = str(result.markdown).strip()

        if not markdown:
            raise ValueError(
                f"Empty content returned from {url}"
            )

        return {
            "url": url,
            "title": title,
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": markdown,
        }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
