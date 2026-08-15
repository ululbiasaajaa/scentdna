from src.orchestrator import IngestionOrchestrator
from src.pipeline import save_and_embed_records

def test_partial_mutation():
    print("=== SCENTDNA PARTIAL UPDATE TEST ===")
    
    # 1. Fetch data normal dari Mykonos
    orchestrator = IngestionOrchestrator()
    report = orchestrator.run_mykonos_pipeline()
    records = report['valid_records']
    
    if not records:
        print("Data kosong, pembatalan pengujian.")
        return

    # 2. Simulasi Mutasi Teks pada 1 Record Pertama
    target_product = records[0]
    original_text = target_product.searchable_text
    print(f"[MUTATION] Mengubah searchable_text pada produk: '{target_product.product_name}'")
    
    # Tambahkan teks buatan untuk mengubah SHA-256 hash
    target_product.searchable_text += " [UPDATED FORMULA 2026: EXTRA VANILLA EXTRACTION]"
    
    # 3. Eksekusi Re-Ingestion
    print("[EXECUTE] Menjalankan save_and_embed_records dengan 1 data ter-mutasi...")
    save_and_embed_records(records)

if __name__ == "__main__":
    test_partial_mutation()