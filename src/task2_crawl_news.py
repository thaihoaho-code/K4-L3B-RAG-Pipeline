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
from datetime import datetime, timezone
from pathlib import Path

from crawl4ai import AsyncWebCrawler


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://baochinhphu.vn/hoa-don-tu-may-tinh-tien-sai-ten-dia-chi-co-phai-lap-lai-102260811155618795.htm",

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
            error_message = getattr(result, "error_message", None)
            detail = f" ({error_message})" if error_message else ""
            raise RuntimeError(f"Crawl failed: {url}{detail}")

        metadata = result.metadata or {}
        title = str(metadata.get("title") or "").strip()
        if not title:
            title = url

        raw_markdown = result.markdown
        if not isinstance(raw_markdown, str) or not raw_markdown.strip():
            raise ValueError(f"Empty content returned from {url}")
        markdown = raw_markdown.strip()

        return {
            "url": url,
            "title": title,
            "date_crawled": datetime.now(timezone.utc).isoformat(),
            "content_markdown": markdown,
        }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if len(set(ARTICLE_URLS)) < 5:
        raise ValueError("ARTICLE_URLS must contain at least 5 unique URLs")

    saved_count = 0
    failures = []

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
            saved_count += 1
        except Exception as error:
            print(f"Failed: {url} — {error}")
            failures.append(url)

    if saved_count < 5:
        raise RuntimeError(
            f"Only {saved_count} articles were saved; at least 5 are required. "
            f"Failed URLs: {', '.join(failures)}"
        )

    print(f"Task 2 completed: {saved_count} articles are ready.")


if __name__ == "__main__":
    asyncio.run(crawl_all())
