import json
import os
import sys

# Menambahkan root directory ke sys.path agar dapat mengimpor modul dari 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.search import ScentSearchEngine

def evaluate_retrieval(top_k: int = 5):
    dataset_path = os.path.join(os.path.dirname(__file__), 'dataset.json')
    
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset tidak ditemukan di {dataset_path}")
        return

    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    engine = ScentSearchEngine()

    total_queries = len(dataset)
    if total_queries == 0:
        print("Dataset kosong.")
        return

    hits = 0
    total_precision = 0.0
    total_recall = 0.0
    reciprocal_ranks = []

    print("==================================================")
    print(f"   SCENTDNA RETRIEVAL EVALUATION (Top-{top_k})     ")
    print("==================================================")

    for item in dataset:
        query = item["query"]
        expected_products = set(item["relevant_products"])
        filters = item.get("filters", {})
        
        # Ekstrak filter jika ada
        min_price = filters.get("min_price")
        max_price = filters.get("max_price")
        brand = filters.get("brand")

        # Panggil ScentSearchEngine langsung secara internal
        retrieved_results = engine.search_similar_perfumes(
            query_text=query,
            top_k=top_k,
            min_price=min_price,
            max_price=max_price,
            brand=brand
        )

        retrieved_names = [res["product_name"] for res in retrieved_results]
        retrieved_set = set(retrieved_names)

        # Hitung Intersection (Produk relevan yang berhasil ditarik)
        relevant_retrieved = expected_products.intersection(retrieved_set)
        num_relevant_retrieved = len(relevant_retrieved)

        # 1. Precision@K = (Relevant & Retrieved) / K
        precision_at_k = num_relevant_retrieved / top_k if top_k > 0 else 0.0
        total_precision += precision_at_k

        # 2. Recall@K = (Relevant & Retrieved) / Total Expected Relevant
        recall_at_k = num_relevant_retrieved / len(expected_products) if len(expected_products) > 0 else 0.0
        total_recall += recall_at_k

        # 3. Hit Rate@K = 1 jika ada setidaknya 1 produk relevan yang ditemukan, else 0
        is_hit = 1 if num_relevant_retrieved > 0 else 0
        hits += is_hit

        # 4. MRR (Mean Reciprocal Rank) = Posisi kemunculan produk relevan pertama
        found_rank = None
        for rank, name in enumerate(retrieved_names, start=1):
            if name in expected_products:
                found_rank = rank
                break
        
        if found_rank:
            reciprocal_ranks.append(1.0 / found_rank)
        else:
            reciprocal_ranks.append(0.0)

        print(f"\n🔎 Query: \"{query}\"")
        print(f"   Expected : {list(expected_products)}")
        print(f"   Retrieved: {retrieved_names}")
        print(f"   -> Precision@{top_k}: {precision_at_k:.2f} | Recall@{top_k}: {recall_at_k:.2f} | Hit: {is_hit}")

    # Kalkulasi Metrik Keseluruhan (Macro Average)
    mean_precision = total_precision / total_queries
    mean_recall = total_recall / total_queries
    hit_rate = hits / total_queries
    mrr = sum(reciprocal_ranks) / total_queries

    print("\n" + "=" * 50)
    print(" EVALUATION SUMMARY RESULTS")
    print("=" * 50)
    print(f"Dataset Size    : {total_queries} queries")
    print(f"Precision@{top_k}    : {mean_precision:.4f}")
    print(f"Recall@{top_k}       : {mean_recall:.4f}")
    print(f"Hit Rate@{top_k}     : {hit_rate:.4f}")
    print(f"MRR             : {mrr:.4f}")
    print("=" * 50)

if __name__ == "__main__":
    evaluate_retrieval(top_k=5)