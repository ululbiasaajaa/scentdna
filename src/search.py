import psycopg
from typing import List, Dict, Any, Optional
from src.config import DATABASE_URL
from src.embedder import TextEmbedder

class ScentSearchEngine:
    def __init__(self):
        self.embedder = TextEmbedder()

    def search_similar_perfumes(
        self, 
        query_text: str, 
        top_k: int = 5, 
        min_price: Optional[float] = None, 
        max_price: Optional[float] = None, 
        brand: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Menerima query teks, embedding, lalu mencari produk mirip di PostgreSQL
        dengan dukungan filter opsional (min_price, max_price, brand).
        """
        if not query_text.strip():
            return []

        # 1. Generate Embedding Vector untuk Query User
        query_vector = self.embedder.generate_embeddings_batch([query_text])[0]
        vector_str = str(query_vector)

        # 2. Susun Dynamic SQL Query dengan pgvector Cosine Distance (<=>)
        query_sql = """
        SELECT 
            product_name,
            source_url,
            price_amount,
            top_notes,
            middle_notes,
            base_notes,
            searchable_text,
            (1 - (embedding <=> %s::vector)) AS similarity_score
        FROM products
        WHERE embedding IS NOT NULL
        """
        
        # Parameter penampung binding SQL
        params = [vector_str]

        # Filter rentang harga minimum (berdasarkan price_amount)
        if min_price is not None:
            query_sql += " AND price_amount >= %s"
            params.append(min_price)

        # Filter rentang harga maksimum (berdasarkan price_amount)
        if max_price is not None:
            query_sql += " AND price_amount <= %s"
            params.append(max_price)

        # Filter pencarian brand/nama produk (case-insensitive ILIKE)
        if brand:
            query_sql += " AND product_name ILIKE %s"
            params.append(f"%{brand}%")

        # Urutan kemiripan vektor & limit
        query_sql += """
        ORDER BY embedding <=> %s::vector ASC
        LIMIT %s;
        """
        # Masukkan vector_str kedua untuk ORDER BY dan top_k untuk LIMIT
        params.extend([vector_str, top_k])

        results = []
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(query_sql, tuple(params))
                rows = cur.fetchall()

                for row in rows:
                    results.append({
                        "product_name": row[0],
                        "source_url": row[1],
                        "price": row[2],
                        "top_notes": row[3],
                        "middle_notes": row[4],
                        "base_notes": row[5],
                        "searchable_text": row[6],
                        "score": round(float(row[7]), 4)
                    })

        return results

def run_cli_test():
    print("==================================================")
    print("    SCENTDNA ADVANCED FILTER SEARCH (CLI TEST)    ")
    print("==================================================")
    
    engine = ScentSearchEngine()

    # Test 1: Search biasa (Regression Test)
    print("\n🔎 TEST 1: Standard Semantic Search (Tanpa Filter)")
    print("-" * 50)
    res_normal = engine.search_similar_perfumes("parfum fresh buat kantor", top_k=2)
    for r in res_normal:
        print(f" • [{r['score']*100:.2f}%] {r['product_name']} | Rp {r['price']:,.0f}" if r['price'] else f" • {r['product_name']}")

    # Test 2: Search dengan filter max_price
    print("\n🔎 TEST 2: Filter Max Price (Maksimal Rp 500.000)")
    print("-" * 50)
    res_price = engine.search_similar_perfumes("parfum manis vanilla", top_k=2, max_price=500000)
    for r in res_price:
        print(f" • [{r['score']*100:.2f}%] {r['product_name']} | Rp {r['price']:,.0f}")

    # Test 3: Search dengan filter brand
    print("\n🔎 TEST 3: Filter Brand ('Mykonos')")
    print("-" * 50)
    res_brand = engine.search_similar_perfumes("aroma mewah", top_k=2, brand="Mykonos")
    for r in res_brand:
        print(f" • [{r['score']*100:.2f}%] {r['product_name']}")

if __name__ == "__main__":
    run_cli_test()