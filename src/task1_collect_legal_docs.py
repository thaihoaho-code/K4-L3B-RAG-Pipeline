"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """
    Các tài liệu pháp lý được tải thủ công từ Công báo Chính phủ
    và lưu tại data/landing/legal/.
    """

    required_files = [
        "luat_108_2025_quan_ly_thue.pdf",
        "nghi_dinh_254_2026_hoa_don_dien_tu.pdf",
        "thong_tu_91_2026_hoa_don_dien_tu.pdf",
    ]

    missing_files = []

    for filename in required_files:
        path = DATA_DIR / filename

        if not path.exists():
            missing_files.append(filename)
        else:
            print(f"Found: {path.name}")

    if missing_files:
        raise FileNotFoundError(
            "Missing legal documents:\n"
            + "\n".join(f"- {name}" for name in missing_files)
        )

    print("Task 1 completed: 3 legal documents are ready.")


if __name__ == "__main__":
    setup_directory()
    download_documents()
