import json
import os
import sys

# Menambahkan root directory ke sys.path agar dapat mengimpor modul dari 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.search import ScentSearchEngine

def evaluate_filters():
    dataset_path = os.path.join(os.path.dirname(__file__), 'dataset.json')
    
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset tidak ditemukan di {dataset_path}")
        return

    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    engine = ScentSearchEngine()

    print("==================================================")
    print("      SCENTDNA ADVANCED FILTER EVALUATION         ")
    print("==================================================")

    total_tests = 0
    passed_tests = 0

    for idx, item in enumerate(dataset, start=1):
        query = item["query"]
        filters = item.get("filters", {})
        
        min_price = filters.get("min_price")
        max_price = filters.get("max_price")
        brand = filters.get("brand")

        # Jika tidak ada filter yang diset pada kueri ini, lewati
        if min_price is None and max_price is None and brand is None:
            continue

        total_tests += 1
        print(f"\n🧪 Test Case #{idx}: Query=\"{query}\"")
        print(f"   Filters -> Min: {min_price} | Max: {max_price} | Brand: {brand}")

        # Panggil pencarian dengan filter
        results = engine.search_similar_perfumes(
            query_text=query,
            top_k=5,
            min_price=min_price,
            max_price=max_price,
            brand=brand
        )

        test_passed = True
        violation_reasons = []

        for res in results:
            product_name = res["product_name"]
            price = res["price"]

            # Cek constraint min_price
            if min_price is not None and (price is None or price < min_price):
                test_passed = False
                violation_reasons.append(f"Harga {price} melanggar min_price ({min_price}) pada produk: {product_name}")

            # Cek constraint max_price
            if max_price is not None and (price is None or price > max_price):
                test_passed = False
                violation_reasons.append(f"Harga {price} melanggar max_price ({max_price}) pada produk: {product_name}")

            # Cek constraint brand (case-insensitive check di product_name)
            if brand is not None and brand.lower() not in product_name.lower():
                test_passed = False
                violation_reasons.append(f"Brand '{brand}' tidak ditemukan pada produk: {product_name}")

        if test_passed:
            passed_tests += 1
            print("   Status: ✅ PASS (Semua hasil mematuhi filter)")
        else:
            print("   Status: ❌ FAIL")
            for reason in violation_reasons:
                print(f"      • Violations: {reason}")

    print("\n" + "=" * 50)
    print(" FILTER EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Total Filterged Tests : {total_tests}")
    print(f"Passed                : {passed_tests}")
    print(f"Failed                : {total_tests - passed_tests}")
    if total_tests > 0 and passed_tests == total_tests:
        print("Result                : 100% COMPLIANT (PASS)")
    else:
        print("Result                : CONSTRAINTS VIOLATED")
    print("=" * 50)

if __name__ == "__main__":
    evaluate_filters()