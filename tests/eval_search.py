from src.search import ScentSearchEngine

def run_retrieval_evaluation():
    print("==================================================")
    print("    SCENTDNA SEARCH EVALUATION & THRESHOLD AUDIT  ")
    print("==================================================\n")
    
    engine = ScentSearchEngine()
    
    # Threshold rekomendasi standar cosine similarity untuk MiniLM-L12
    SIMILARITY_THRESHOLD = 0.40 # 40% kemiripan minimal
    
    eval_queries = [
        {"query": "parfum aroma kopi coffe hangat", "expected_keyword": "coffee"},
        {"query": "bau pantai laut segar citrus aquatic", "expected_keyword": "fresh"},
        {"query": "parfum aroma melati jasmine floral putih", "expected_keyword": "jasmine"},
        {"query": "wanginya cowok maskulin kayu oud wood", "expected_keyword": "wood"}
    ]

    for item in eval_queries:
        q = item["query"]
        print(f"📌 TEST QUERY: \"{q}\"")
        results = engine.search_similar_perfumes(q, top_k=5)
        
        valid_hits = 0
        for idx, res in enumerate(results, start=1):
            score = res["score"]
            is_above_threshold = score >= SIMILARITY_THRESHOLD
            status_tag = "✅ PASS" if is_above_threshold else "⚠️ LOW MATCH"
            
            if is_above_threshold:
                valid_hits += 1
                
            score_percent = f"{score * 100:.2f}%"
            print(f"   {idx}. [{score_percent}] {res['product_name']} -> {status_tag}")
        
        print(f"   📊 Precision@5 (Above Threshold {SIMILARITY_THRESHOLD*100:.0f}%): {valid_hits}/5 Relevant\n")
        print("-" * 60)

if __name__ == "__main__":
    run_retrieval_evaluation()