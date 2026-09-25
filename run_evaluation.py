import json
import os
import pandas as pd
from pathlib import Path
from datasets import Dataset

from ragas import evaluate
from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy,
    ContextRecall,
    ContextPrecision,
)

# Cấu hình để Ragas dùng Gemini thay vì OpenAI (do bạn đang dùng Gemini API)
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from src.task10_generation import generate_with_citation

GOLDEN_DATASET_PATH = Path("group_project/evaluation/golden_dataset.json")

def load_dataset():
    with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_ragas_dataset(golden_data, use_reranking: bool):
    data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }
    
    print("Đang tạo câu trả lời từ RAG Pipeline...")
    for idx, item in enumerate(golden_data):
        print(f"[{idx+1}/{len(golden_data)}] Xử lý câu hỏi: {item['question']}")
        
        # Gọi RAG
        result = generate_with_citation(
            query=item["question"], 
            top_k=5, 
            use_reranking=use_reranking
        )
        
        # Trích xuất chunks context
        contexts = [chunk["content"] for chunk in result["sources"]]
        
        data["question"].append(item["question"])
        data["answer"].append(result["answer"])
        data["contexts"].append(contexts)
        data["ground_truth"].append(item["expected_answer"])
        
    return Dataset.from_dict(data)

def run_eval_for_config(config_name: str, use_reranking: bool):
    print(f"\n{'='*50}")
    print(f"BẮT ĐẦU ĐÁNH GIÁ: {config_name}")
    print(f"{'='*50}")
    
    golden_data = load_dataset()
    dataset = build_ragas_dataset(golden_data, use_reranking)
    
    print("\nĐang chạy RAGAS để đo lường 4 metrics...")
    
    # Khởi tạo LLM và Embeddings của Gemini cho Ragas Evaluator
    gemini_llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
    gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    result = evaluate(
        dataset,
        metrics=[Faithfulness(), AnswerRelevancy(), ContextRecall(), ContextPrecision()],
        llm=gemini_llm,
        embeddings=gemini_embeddings
    )
    
    print(f"\nKẾT QUẢ {config_name}:")
    print(result)
    
    # Lưu ra file CSV
    df = result.to_pandas()
    df.to_csv(f"group_project/evaluation/result_{config_name.replace(' ', '_')}.csv", index=False)
    print(f"Đã lưu chi tiết vào group_project/evaluation/result_{config_name.replace(' ', '_')}.csv")

if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        print("Vui lòng set GEMINI_API_KEY trong .env")
        exit(1)
        
    # Chạy Config A
    # run_eval_for_config("Config A - Dense Only", use_reranking=False)
    
    # Chạy Config B
    run_eval_for_config("Config B - Hybrid RRF", use_reranking=True)
    
    print("\nHOÀN TẤT A/B TESTING! Vui lòng cập nhật RESULT.md dựa trên số điểm thực tế trên màn hình.")
