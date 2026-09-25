"""Chuẩn hóa dữ liệu landing thành Markdown có metadata truy nguyên."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def _clean_markdown(value: str) -> str:
    value = value.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def _yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _read_legal_manifest() -> dict[str, dict[str, str]]:
    manifest_path = LANDING_DIR / "legal" / "sources.json"
    if not manifest_path.exists():
        return {}
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        item["local_file"]: item
        for item in data.get("sources", [])
        if item.get("local_file")
    }


def _convert_with_markitdown(path: Path) -> str:
    """Use MarkItDown when installed, with a small dependency-light fallback."""
    try:
        from markitdown import MarkItDown
    except ImportError:
        return _fallback_extract(path)

    result = MarkItDown().convert(str(path))
    text = getattr(result, "text_content", None)
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"MarkItDown trả về nội dung rỗng: {path}")
    return text


def _fallback_extract(path: Path) -> str:
    """Fallback cho môi trường chưa cài MarkItDown.

    PDF dùng pypdf (đã được khai báo gián tiếp trong workflow PDF); DOCX dùng
    XML trong gói Office Open XML. Khi chạy theo pyproject, MarkItDown vẫn là
    bộ chuyển đổi ưu tiên.
    """
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as error:
            raise RuntimeError(
                "Cần cài markitdown[pdf] hoặc pypdf để chuyển PDF sang Markdown"
            ) from error
        pages = [page.extract_text() or "" for page in PdfReader(str(path)).pages]
        return "\n\n".join(pages)

    if suffix == ".docx":
        with ZipFile(path) as archive:
            document_xml = archive.read("word/document.xml")
        root = ElementTree.fromstring(document_xml)
        paragraphs: list[str] = []
        current: list[str] = []
        for element in root.iter():
            local_name = element.tag.rsplit("}", 1)[-1]
            if local_name == "t" and element.text:
                current.append(element.text)
            elif local_name == "p" and current:
                paragraphs.append("".join(current))
                current = []
        if current:
            paragraphs.append("".join(current))
        return "\n\n".join(paragraphs)

    raise RuntimeError(f"Không có bộ chuyển đổi fallback cho {path.suffix}: {path}")


def _frontmatter(metadata: dict[str, str]) -> str:
    rows = ["---"]
    for key, value in metadata.items():
        rows.append(f"{key}: {_yaml_string(value)}")
    rows.extend(["---", ""])
    return "\n".join(rows)


def _remove_duplicate_title(content: str, title: str) -> str:
    lines = content.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines:
        first = re.sub(r"^#+\s*", "", lines[0]).strip()
        if first.casefold() == title.strip().casefold():
            lines.pop(0)
    return "\n".join(lines).strip()


def convert_legal_docs() -> None:
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = _read_legal_manifest()
    paths = sorted(
        path
        for path in legal_dir.iterdir()
        if path.is_file() and not path.name.startswith(".") and path.suffix.lower() in {".pdf", ".doc", ".docx"}
    )
    if not paths:
        raise FileNotFoundError(f"Không có PDF/DOC/DOCX trong {legal_dir}")

    converted_at = datetime.now(timezone.utc).isoformat()
    for path in paths:
        item = manifest.get(path.name, {})
        title = item.get("title", path.stem.replace("_", " "))
        content = _clean_markdown(_convert_with_markitdown(path))
        if len(content) < 200:
            raise ValueError(f"Nội dung legal quá ngắn sau khi convert: {path}")
        metadata = {
            "title": title,
            "doc_type": "legal",
            "source_file": path.name,
            "source_url": item.get("url", ""),
            "converted_at": converted_at,
        }
        output = output_dir / f"{path.stem}.md"
        body = f"# {title}\n\n{content}\n"
        output.write_text(_frontmatter(metadata) + body, encoding="utf-8")
        print(f"Saved: {output}")


def convert_news_articles() -> None:
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = sorted(news_dir.glob("*.json"))
    if not paths:
        raise FileNotFoundError(f"Không có JSON bài viết trong {news_dir}")

    required = {"url", "title", "date_crawled", "content_markdown"}
    converted_at = datetime.now(timezone.utc).isoformat()
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        missing = required - data.keys()
        if missing:
            raise ValueError(f"{path.name} thiếu metadata: {sorted(missing)}")
        content = _clean_markdown(str(data["content_markdown"]))
        content = _remove_duplicate_title(content, str(data["title"]))
        if len(content) < 200:
            raise ValueError(f"Nội dung bài viết quá ngắn: {path}")
        metadata = {
            "title": str(data["title"]).strip(),
            "doc_type": "news",
            "source_file": path.name,
            "source_url": str(data["url"]).strip(),
            "date_crawled": str(data["date_crawled"]).strip(),
            "converted_at": converted_at,
        }
        output = output_dir / f"{path.stem}.md"
        body = f"# {metadata['title']}\n\n{content}\n"
        output.write_text(_frontmatter(metadata) + body, encoding="utf-8")
        print(f"Saved: {output}")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
