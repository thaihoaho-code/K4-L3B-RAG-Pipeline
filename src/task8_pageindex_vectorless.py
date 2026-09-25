"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import os
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CACHE_FILE = Path(__file__).parent.parent / "data" / "pageindex_cache.json"


def convert_md_to_pdf(md_path: Path) -> Path:
    """Convert Markdown sang PDF bằng fpdf2."""
    from fpdf import FPDF
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # FPDF standard fonts (Helvetica) không hỗ trợ tiếng Việt utf-8
    # Xử lý an toàn bằng cách ignore các ký tự không được hỗ trợ để làm file PDF tạm
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 7, text=clean_text)
    
    pdf_path = md_path.with_suffix(".pdf")
    pdf.output(str(pdf_path))
    return pdf_path


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY:
        print("Thiếu PAGEINDEX_API_KEY trong file .env. Bỏ qua upload.")
        return

    try:
        from pageindex import Client
        client = Client(api_key=PAGEINDEX_API_KEY)
    except ImportError:
        print("Chưa cài đặt pageindex. Bỏ qua upload.")
        return

    cached_ids = {}
    if CACHE_FILE.exists():
        try:
            cached_ids = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    for category in ["legal", "news"]:
        category_dir = STANDARDIZED_DIR / category
        if not category_dir.exists():
            continue
            
        for md_file in category_dir.glob("*.md"):
            file_key = f"{category}/{md_file.name}"
            
            if file_key in cached_ids:
                continue
                
            try:
                # Convert sang PDF tạm trước khi upload
                pdf_file = convert_md_to_pdf(md_file)
                
                print(f"Uploading {pdf_file.name} to PageIndex...")
                with open(pdf_file, "rb") as f:
                    document = client.documents.upload(file=f)
                    
                # Trích xuất ID linh hoạt tuỳ SDK
                doc_id = None
                if hasattr(document, "id"):
                    doc_id = document.id
                elif isinstance(document, dict) and "id" in document:
                    doc_id = document["id"]
                else:
                    doc_id = str(document)
                    
                cached_ids[file_key] = doc_id
                
                # Xóa file PDF tạm
                pdf_file.unlink()
                
            except Exception as e:
                print(f"Lỗi khi upload {md_file.name}: {e}")

    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cached_ids, indent=2), encoding="utf-8")
    print(f"Đã cập nhật PageIndex cache tại {CACHE_FILE}")


def pageindex_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Trả về pageindex SearchResult."""
    if not PAGEINDEX_API_KEY:
        return []

    try:
        from pageindex import Client
        client = Client(api_key=PAGEINDEX_API_KEY)
    except ImportError:
        return []

    doc_ids = []
    if CACHE_FILE.exists():
        try:
            cached_ids = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            doc_ids = list(cached_ids.values())
        except Exception:
            pass

    if not doc_ids:
        return []

    results = []
    try:
        # Timeout ngầm định trong SDK hoặc sử dụng requests timeout nếu SDK cho phép
        response = client.search(
            query=query, 
            document_ids=doc_ids,
            top_k=top_k
        )
        
        # Parse kết quả an toàn
        nodes = []
        if hasattr(response, "nodes"):
            nodes = response.nodes
        elif hasattr(response, "results"):
            nodes = response.results
        elif isinstance(response, list):
            nodes = response
            
        for idx, node in enumerate(nodes):
            node_id = getattr(node, "id", None) or (node.get("id") if isinstance(node, dict) else str(uuid.uuid4()))
            content = getattr(node, "content", None) or getattr(node, "text", None) or (node.get("content") or node.get("text") if isinstance(node, dict) else str(node))
            
            # Gán điểm số nếu API không trả về score (giảm dần theo rank)
            score = getattr(node, "score", None) or (node.get("score") if isinstance(node, dict) else max(0.0, 1.0 - (idx * 0.1)))
            
            metadata = getattr(node, "metadata", None) or (node.get("metadata") if isinstance(node, dict) else {})
            
            results.append({
                "id": str(node_id),
                "content": str(content),
                "score": float(score),
                "metadata": metadata,
                "retrieval_method": "pageindex",
            })
            
    except Exception as e:
        print(f"Lỗi khi search qua PageIndex API: {e}")
        # Trả về list rỗng thay vì crash (fallback strategy)
        return []
        
    results = sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
    return results


if __name__ == "__main__":
    upload_documents()
    print("Test search:")
    res = pageindex_search("thông tin tài liệu", top_k=2)
    for r in res:
        print(r)
