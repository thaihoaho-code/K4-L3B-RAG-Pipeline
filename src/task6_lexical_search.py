"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""


CORPUS: list[dict] = []


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    # TODO: Tokenize và tạo BM25 index.
    #
    from rank_bm25 import BM25Okapi
    tokenized = [item["content"].lower().split() for item in corpus]
    return BM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    import numpy as np
    
    global CORPUS
    if not CORPUS:
        from .task4_chunking_indexing import get_collection
        collection = get_collection()
        data = collection.get(include=["documents", "metadatas"])
        if data and data["ids"]:
            for idx, doc, meta in zip(data["ids"], data["documents"], data["metadatas"]):
                CORPUS.append({"id": idx, "content": doc, "metadata": meta})
    
    if not CORPUS:
        return []
        
    bm25 = build_bm25_index(CORPUS)
    scores = bm25.get_scores(query.lower().split())
    indices = np.argsort(scores)[::-1][:top_k]
    results = []
    for index in indices:
        if scores[index] <= 0:
            continue
        item = CORPUS[index]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(scores[index]),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })
    return results


if __name__ == "__main__":
    for result in lexical_search("Định dạng hóa đơn điện tử", top_k=3):
        print(result)
