import psycopg
from src.config import DATABASE_URL

def verify_database_state():
    print("=== SCENTDNA DB VERIFICATION ===")
    
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            # 1. Hitung total record
            cur.execute("SELECT COUNT(*) FROM products;")
            total_count = cur.fetchone()[0]
            
            # 2. Hitung record yang punya embedding & hash
            cur.execute("""
                SELECT 
                    COUNT(embedding) AS embedded_count,
                    COUNT(searchable_text_hash) AS hashed_count
                FROM products;
            """)
            embedded_count, hashed_count = cur.fetchone()
            
            # 3. Ambil sampel 1 record untuk verifikasi dimensi vector
            cur.execute("""
                SELECT product_name, searchable_text_hash, vector_dims(embedding), embedding 
                FROM products 
                LIMIT 1;
            """)
            sample = cur.fetchone()
            
            print(f"- Total Produk di DB     : {total_count}")
            print(f"- Produk Ber-Vector     : {embedded_count}")
            print(f"- Produk Ber-Hash SHA256: {hashed_count}\n")
            
            if sample:
                name, text_hash, dims, vector_raw = sample
                # Konversi string vector pgvector ke list float untuk sampel awal
                vector_preview = str(vector_raw)[:45] + "..." if vector_raw else "None"
                print("[SAMPLE RECORD CHECK]:")
                print(f"  • Nama Produk : {name}")
                print(f"  • SHA-256 Hash: {text_hash}")
                print(f"  • Dimensi Vector: {dims} (Expected: 384)")
                print(f"  • Vector Output : {vector_preview}")

if __name__ == "__main__":
    verify_database_state()