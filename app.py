"""Streamlit UI for the electronic-invoice legal RAG assistant."""

from __future__ import annotations

import logging
import html
import re
from typing import Any

import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation, reorder_for_llm


load_dotenv()
LOGGER = logging.getLogger(__name__)

st.set_page_config(
    page_title="Trợ lý xử lý hóa đơn điện tử",
    page_icon="⚖️",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        color-scheme: light;
        --ink: #202124;
        --muted: #5f6368;
        --accent: #176b52;
        --line: #e2e4e7;
        --surface: #ffffff;
        --canvas: #f7f8f8;
    }
    [data-testid="stAppViewContainer"] {
        background: var(--canvas) !important;
        color: var(--ink) !important;
        color-scheme: light;
    }
    [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"],
    [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] * {
        color: var(--ink) !important;
    }
    [data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"],
    [data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] * {
        color: var(--muted) !important;
    }
    [data-testid="stHeader"] { background: var(--canvas); }
    [data-testid="stSidebar"] {
        background: #f0f2f1;
        border-right: 1px solid #e1e4e2;
        color: var(--ink) !important;
    }
    [data-testid="stSidebar"] * { color: var(--ink) !important; }
    .block-container { max-width: 1120px; padding: 2rem 2.5rem 5rem; }
    .app-header { margin: 0.25rem 0 2rem; }
    .app-badge {
        display: inline-block;
        margin: 0 0 0.9rem;
        padding: 0.38rem 0.7rem;
        border: 1px solid #d8e4de;
        border-radius: 999px;
        background: #edf4f0;
        color: #315c4a !important;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .app-title {
        margin: 0;
        color: #202124 !important;
        font-size: clamp(1.8rem, 3vw, 2.35rem);
        font-weight: 650;
        letter-spacing: -0.035em;
        line-height: 1.2;
    }
    .app-subtitle {
        max-width: 780px;
        margin: 0.65rem 0 0;
        color: #5f6368 !important;
        font-size: 1rem;
        line-height: 1.6;
    }
    .system-status {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        margin: 0.9rem 0 1.15rem;
        padding: 0.55rem 0.7rem;
        border: 1px solid #dfe8e2;
        border-radius: 10px;
        background: #f7fbf8;
        color: #32624f !important;
        font-size: 0.82rem;
    }
    .system-dot {
        width: 0.48rem;
        height: 0.48rem;
        border-radius: 50%;
        background: #2b9a70;
        box-shadow: 0 0 0 3px rgba(43, 154, 112, 0.13);
    }
    [data-testid="stChatMessage"] {
        margin: 0.55rem 0;
        padding: 0.75rem 1rem;
        border: 1px solid transparent;
        border-radius: 16px;
        background: transparent !important;
        box-shadow: none;
        color: var(--ink) !important;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] * {
        color: var(--ink) !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        max-width: 94%;
        margin-left: auto;
        background: #ecefed !important;
        border-color: #e1e5e2;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        border-color: transparent;
    }
    [data-testid="stChatInput"] textarea {
        min-height: 62px;
        padding: 0.95rem 3.5rem 0.9rem 1.1rem;
        border: 1px solid #cfd6d2;
        border-radius: 18px;
        background: var(--surface) !important;
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink);
        box-shadow: 0 8px 24px rgba(39, 65, 54, 0.09);
        font-size: 0.98rem;
        line-height: 1.45;
    }
    [data-testid="stChatInput"] textarea::placeholder { color: #73777d !important; }
    [data-testid="stChatInput"] textarea:focus {
        border-color: #7da994;
        box-shadow: 0 0 0 3px rgba(23, 107, 82, 0.1);
    }
    [data-testid="stChatInput"] button {
        right: 0.65rem;
        bottom: 0.68rem;
        width: 2.15rem;
        height: 2.15rem;
        border-radius: 11px;
        background: #176b52 !important;
        color: #fff !important;
    }
    [data-testid="stChatInput"] button:hover { background: #0d553f !important; }
    [data-testid="stChatInput"] button svg { color: #fff !important; }
    [data-testid="stChatInput"]::before {
        display: block;
        margin: 0 0 0.45rem 0.25rem;
        color: #68746e;
        content: "Enter để gửi · Nội dung được trả lời dựa trên corpus pháp lý";
        font-size: 0.76rem;
    }
    [data-testid="stExpander"] {
        margin: 0.35rem 0;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: #fff !important;
        color: var(--ink) !important;
    }
    [data-testid="stExpander"] * { color: var(--ink) !important; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        margin: 0.55rem 0;
        border-color: #dfe6e1 !important;
        border-radius: 14px !important;
        background: #fff !important;
        box-shadow: 0 4px 14px rgba(36, 63, 51, 0.045);
    }
    .citation-heading {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin-bottom: 0.15rem;
    }
    .citation-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 1.7rem;
        height: 1.7rem;
        border-radius: 8px;
        background: #e8f2ed;
        color: #176b52 !important;
        font-size: 0.78rem;
        font-weight: 750;
    }
    .citation-name {
        color: #263a31 !important;
        font-size: 0.94rem;
        font-weight: 680;
    }
    .citation-meta-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
        margin: 0.35rem 0 0.15rem 2.25rem;
    }
    .citation-chip {
        padding: 0.2rem 0.48rem;
        border: 1px solid #e0e8e2;
        border-radius: 999px;
        background: #f7faf8;
        color: #64736b !important;
        font-size: 0.73rem;
    }
    [data-testid="stLinkButton"] a {
        border: 1px solid #cbded5;
        border-radius: 9px;
        background: #f1f6f3;
        color: #145b45 !important;
    }
    div.stButton > button {
        min-height: 2.7rem;
        border: 1px solid #dfe2e0;
        border-radius: 11px;
        background: #fff !important;
        color: #27312d !important;
        text-align: left;
        white-space: normal;
    }
    div.stButton > button:hover {
        border-color: #9db9aa;
        background: #f2f6f3 !important;
        color: #174f3d !important;
    }
    [data-testid="stWidgetLabel"] * { color: #34383d !important; }
    .section-label {
        margin: 1rem 0 0.35rem;
        color: #353a37 !important;
        font-size: 0.93rem;
        font-weight: 650;
    }
    .suggestions-caption {
        margin: -0.15rem 0 0.75rem;
        color: #6b7370 !important;
        font-size: 0.88rem;
    }
    .citation-card {
        margin: 0.4rem 0;
        padding: 0.8rem 0.95rem;
        border: 1px solid #e2e6e3;
        border-radius: 12px;
        background: #fff;
    }
    .citation-title { margin: 0; color: #26332d !important; font-weight: 650; }
    .citation-meta { margin: 0.25rem 0 0; color: #66716b !important; font-size: 0.84rem; }
    @media (max-width: 700px) {
        .block-container { padding: 1.1rem 1rem 4rem; }
        .app-header { margin-bottom: 1.25rem; }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { max-width: 100%; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "top_k" not in st.session_state:
    st.session_state.top_k = 5


SUGGESTED_QUESTIONS = [
    "Hóa đơn điện tử sai tên, địa chỉ người mua thì xử lý thế nào?",
    "Khi nào phải lập hóa đơn thay thế?",
    "Khi nào được lập hóa đơn điều chỉnh?",
    "Hóa đơn từ máy tính tiền bị lập sai thì xử lý ra sao?",
    "Quy định tại Điều 10 Thông tư 91/2026/TT-BTC là gì?",
    "Hóa đơn lập trước ngày 01/07/2026 được xử lý như thế nào?",
]


def render_header() -> None:
    st.markdown(
        """
        <header class="app-header">
            <div class="app-badge">Powered by RAG · Hybrid Retrieval · Legal Corpus</div>
            <h1 class="app-title">Trợ lý xử lý hóa đơn điện tử</h1>
            <p class="app-subtitle">Chatbot hỗ trợ tra cứu quy định và hướng xử lý hóa đơn điện tử có sai sót, với căn cứ pháp lý để đối chiếu.</p>
        </header>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.title("Tra cứu pháp lý")
        st.caption(
            "Trợ lý RAG tìm kiếm trong bộ tài liệu pháp luật về hóa đơn điện tử "
            "và trình bày căn cứ liên quan đến câu hỏi."
        )
        st.markdown(
            '<div class="system-status"><span class="system-dot"></span>Hệ thống sẵn sàng tra cứu</div>',
            unsafe_allow_html=True,
        )

        st.markdown("**Phạm vi dữ liệu**")
        st.caption("Quy định về hóa đơn điện tử và xử lý hóa đơn có sai sót.")

        st.markdown("**Nguồn chính**")
        st.markdown(
            "- Luật 108/2025/QH15\n"
            "- Nghị định 254/2026/NĐ-CP\n"
            "- Thông tư 91/2026/TT-BTC"
        )

        st.slider("Số đoạn truy xuất (top_k)", min_value=3, max_value=10, key="top_k")
        if st.button("Xóa cuộc trò chuyện", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def citation_order(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Use the same ordering that Task 10 uses when numbering context sources."""
    return reorder_for_llm(sources)


def has_valid_citation(answer: str, sources: list[dict[str, Any]]) -> bool:
    """Return true only when a non-refusal answer cites an available document."""
    if not answer or not sources:
        return False

    normalized_answer = answer.casefold()
    refusal_phrases = (
        "tôi không thể xác minh",
        "không thể xác minh thông tin",
        "không tìm thấy thông tin",
        "không tìm thấy nội dung",
        "không có đủ thông tin",
        "không đủ thông tin để trả lời",
        "không thể trả lời dựa trên",
        "không cung cấp thông tin về",
        "i cannot verify",
        "i can't verify",
        "i don't have enough information",
        "not enough information to answer",
    )
    if any(phrase in normalized_answer for phrase in refusal_phrases):
        return False

    cited_numbers = re.findall(
        r"\[\s*Document\s+(\d+)\s*\]", answer, re.IGNORECASE
    )
    return any(1 <= int(number) <= len(sources) for number in cited_numbers)


def render_sources(
    sources: list[dict[str, Any]],
    key_prefix: str,
) -> None:
    """Render citation metadata and genuine source links only."""
    if not sources:
        return

    st.markdown('<div class="section-label">Căn cứ / Nguồn tham khảo</div>', unsafe_allow_html=True)
    for index, source in enumerate(citation_order(sources), 1):
        metadata = source.get("metadata")
        metadata = metadata if isinstance(metadata, dict) else {}
        title = metadata.get("title")
        source_name = metadata.get("source")
        retrieval_method = source.get("retrieval_method")

        with st.container(border=True):
            citation_label = f"[Document {index}]"
            display_name = title or source_name
            title_text = str(display_name) if display_name else "Tài liệu không có tên"

            details = []
            if source_name:
                details.append(f"Tài liệu · {source_name}")
            doc_type = metadata.get("doc_type")
            if doc_type:
                details.append(f"Loại · {doc_type}")
            chunk_index = metadata.get("chunk_index")
            if isinstance(chunk_index, int) and not isinstance(chunk_index, bool):
                details.append(f"Chunk · {chunk_index}")
            if retrieval_method:
                method_labels = {
                    "dense": "semantic",
                    "bm25": "bm25",
                    "pageindex": "pageindex",
                    "hybrid": "hybrid",
                }
                details.append(
                    f"Retrieval · {method_labels.get(retrieval_method, retrieval_method)}"
                )
            score = source.get("score")
            if isinstance(score, (int, float)) and not isinstance(score, bool):
                details.append(f"Score · {score:.4f}")

            heading_html = (
                '<div class="citation-heading">'
                f'<span class="citation-number">{index}</span>'
                f'<span class="citation-name">{html.escape(citation_label)} · '
                f'{html.escape(title_text)}</span>'
                '</div>'
            )
            st.markdown(heading_html, unsafe_allow_html=True)
            if details:
                chips = "".join(
                    f'<span class="citation-chip">{html.escape(str(detail))}</span>'
                    for detail in details
                )
                st.markdown(
                    f'<div class="citation-meta-row">{chips}</div>',
                    unsafe_allow_html=True,
                )

            url = metadata.get("url")
            if isinstance(url, str) and url.startswith(("https://", "http://")):
                st.link_button(
                    "Mở tài liệu gốc",
                    url,
                    key=f"{key_prefix}-source-link-{index}-{source.get('id', index)}",
                )


def render_retrieval_context(
    sources: list[dict[str, Any]],
) -> None:
    """Show the actual retrieved passages without inventing extra context."""
    passages = [
        source for source in citation_order(sources)
        if isinstance(source.get("content"), str) and source["content"].strip()
    ]
    if not passages:
        return

    with st.expander("Context truy xuất", expanded=False):
        for index, source in enumerate(passages, 1):
            st.markdown(f"**[Document {index}]**")
            st.markdown(source["content"].strip())
            if index < len(passages):
                st.divider()


def render_message(message: dict[str, Any], message_index: int) -> None:
    role = message.get("role", "assistant")
    with st.chat_message(role):
        if message.get("error"):
            st.error(message.get("content", "Không thể xử lý câu hỏi lúc này."))
            return

        if role == "assistant":
            st.markdown("**Trả lời**")
        st.markdown(message.get("content", ""))

        if role != "assistant":
            return

        sources = message.get("sources") or []
        answer = message.get("content", "")
        if not has_valid_citation(answer, sources):
            return

        render_sources(sources, f"message-{message_index}")
        render_retrieval_context(sources)


def render_suggested_questions() -> str | None:
    """Render clickable sample questions; return the selected question."""
    st.markdown('<div class="section-label">Câu hỏi gợi ý</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="suggestions-caption">Chọn một câu hỏi để bắt đầu tra cứu.</div>',
        unsafe_allow_html=True,
    )
    selected_question = None
    columns = st.columns(2)
    for index, question in enumerate(SUGGESTED_QUESTIONS):
        with columns[index % 2]:
            if st.button(
                question,
                key=f"suggested-question-{index}",
                use_container_width=True,
            ):
                selected_question = question
    return selected_question


def process_question(query: str, message_index: int) -> None:
    """Retrieve, answer, render, and persist one user question."""
    user_message = {"role": "user", "content": query}
    st.session_state.messages.append(user_message)
    render_message(user_message, message_index)

    with st.chat_message("assistant"):
        with st.spinner("Đang truy xuất căn cứ pháp lý và tạo câu trả lời..."):
            try:
                result = generate_with_citation(
                    query,
                    top_k=st.session_state.top_k,
                )
                assistant_message = {
                    "role": "assistant",
                    "content": result.get("answer")
                    or "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
                    "sources": result.get("sources") or [],
                    "retrieval_source": result.get("retrieval_source", "none"),
                }
            except Exception:
                LOGGER.exception("RAG pipeline failed while answering a question")
                assistant_message = {
                    "role": "assistant",
                    "content": (
                        "Hiện chưa thể xử lý câu hỏi. Vui lòng thử lại sau hoặc "
                        "kiểm tra cấu hình mô hình và dữ liệu đã được lập chỉ mục."
                    ),
                    "sources": [],
                    "retrieval_source": "none",
                    "error": True,
                }

        render_message(assistant_message, message_index + 1)

    st.session_state.messages.append(assistant_message)


def main() -> None:
    render_sidebar()
    render_header()

    selected_question = None
    if not st.session_state.messages:
        selected_question = render_suggested_questions()

    for message_index, message in enumerate(st.session_state.messages):
        render_message(message, message_index)

    typed_query = st.chat_input(
        "Ví dụ: Hóa đơn sai tên người mua thì xử lý thế nào?"
    )
    query = typed_query or selected_question
    if query and query.strip():
        process_question(query.strip(), len(st.session_state.messages))


main()
