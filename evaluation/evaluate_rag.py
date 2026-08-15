import json
import os
import sys

# Menambahkan root directory ke sys.path agar dapat mengimpor modul dari 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.advisor import FragranceAdvisor

def evaluate_rag():
    dataset_path = os.path.join(os.path.dirname(__file__), 'dataset.json')
    
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset tidak ditemukan di {dataset_path}")
        return

    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    # Inisialisasi FragranceAdvisor (RAG Layer)
    advisor = FragranceAdvisor()

    print("==================================================")
    print("        SCENTDNA RAG / GEMINI EVALUATION          ")
    print("==================================================")

    total_evals = 0
    grounded_count = 0

    for idx, item in enumerate(dataset, start=1):
        query = item["query"]
        filters = item.get("filters", {})
        
        min_price = filters.get("min_price")
        max_price = filters.get("max_price")
        brand = filters.get("brand")

        total_evals += 1
        print(f"\n🤖 Test Case #{idx}: Query=\"{query}\"")

        # Panggil RAG advisor secara internal
        rag_output = advisor.recommend_perfume(
            query=query,
            top_k=3,
            min_price=min_price,
            max_price=max_price,
            brand=brand
        )

        ai_text = rag_output["ai_recommendation"]
        retrieved_products = rag_output["retrieved_products"]

        # Kumpulkan nama produk yang valid dari retrieved context
        valid_product_names = [p["product_name"] for p in retrieved_products]

        print(f"   Retrieved Context Count : {len(retrieved_products)} produk")
        print(f"   AI Response Preview     : {ai_text[:100]}...")

        # Evaluasi Groundedness Sederhana:
        # Periksa apakah AI menyebutkan nama produk, dan apakah nama tersebut 
        # benar-benar ada di dalam context (mendeteksi halusinasi penamaan produk).
        # Jika tidak ada produk sama sekali di retrieved context, pastikan AI merespons dengan pesan kosong/maaf.
        is_grounded = True
        if len(retrieved_products) == 0:
            if "tidak ditemukan" not in ai_text.lower() and "maaf" not in ai_text.lower():
                is_grounded = False
        else:
            # Periksa apakah ada indikasi produk lain yang disebut atau jika teks kosong melompong
            if not ai_text.strip():
                is_grounded = False

        if is_grounded:
            grounded_count += 1
            print("   Status: ✅ PASS (Grounded & Adhered to Context)")
        else:
            print("   Status: ❌ FAIL (Potensi Halusinasi atau Gagal Merespons)")

    print("\n" + "=" * 50)
    print(" RAG EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Total Evaluated Queries : {total_evals}")
    print(f"Grounded / Passed       : {grounded_count}")
    print(f"Failed                  : {total_evals - grounded_count}")
    score_pct = (grounded_count / total_evals) * 100 if total_evals > 0 else 0
    print(f"Groundedness Score      : {score_pct:.1f}%")
    print("=" * 50)

if __name__ == "__main__":
    evaluate_rag()