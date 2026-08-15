from typing import List
from src.orchestrator import IngestionOrchestrator
from src.embedder import TextEmbedder
from src.db import init_db, fetch_existing_hashes, upsert_canonical_products

def save_and_embed_records(canonical_records: list):
    """Fungsi persistensi DB + Hash-First Batch Embedding."""
    init_db()
    
    if not canonical_records:
        return

    source_name = canonical_records[0].source_name
    source_ids = [rec.source_id for rec in canonical_records]
    
    # 1. HASH-FIRST PRE-CHECK DB
    existing_db_map = fetch_existing_hashes(source_name, source_ids)
    
    embedder = TextEmbedder()
    
    items_to_embed_indices = []
    texts_to_embed = []
    prepared_payloads = []

    # 2. Identifikasi record yang BENAR-BENAR butuh model inference
    for idx, rec in enumerate(canonical_records):
        current_hash = embedder.compute_hash(rec.searchable_text)
        existing_hash, has_embedding = existing_db_map.get(rec.source_id, (None, False))
        
        # Check True Idempotency:
        if existing_hash == current_hash and has_embedding:
            # Hash SAMA & Vektor ADA -> SKIP MODEL INFERENCE TOTAL
            payload_embedding = None
        else:
            # Data Baru / Hash Beda / Vektor Kosong -> Antrikan untuk Batch Inference
            items_to_embed_indices.append(idx)
            texts_to_embed.append(rec.searchable_text)
            payload_embedding = None
        
        prepared_payloads.append({
            "source_name": rec.source_name,
            "source_id": rec.source_id,
            "source_url": rec.source_url,
            "product_name": rec.product_name,
            "searchable_text": rec.searchable_text,
            "price_amount": rec.price_amount,
            "is_available": rec.is_available,
            "top_notes": rec.top_notes,
            "middle_notes": rec.middle_notes,
            "base_notes": rec.base_notes,
            "image_url": rec.image_url,
            "searchable_text_hash": current_hash,
            "embedding": payload_embedding
        })

    # 3. BATCH EMBEDDING INFERENCE (Hanya untuk data yang butuh)
    if texts_to_embed:
        print(f"\n[EMBEDDER] Generating batch embeddings for {len(texts_to_embed)} items...")
        vectors = embedder.generate_embeddings_batch(texts_to_embed, batch_size=32)
        for list_idx, target_idx in enumerate(items_to_embed_indices):
            prepared_payloads[target_idx]["embedding"] = vectors[list_idx]
    else:
        print("\n[EMBEDDER] All records are up-to-date. Skipping model inference 100%!")

    # 4. UPSERT KE POSTGRESQL
    upsert_canonical_products(prepared_payloads)
    print(f"[SUCCESS] Successfully persisted & embedded {len(prepared_payloads)} records to PostgreSQL.")

def test_orchestrator():
    print("=== SCENTDNA INGESTION ORCHESTRATOR TEST ===")
    print("Menjalankan Ingestion Pipeline secara terpusat...\n")
    
    orchestrator = IngestionOrchestrator()
    report = orchestrator.run_mykonos_pipeline()
    
    print("[SUCCESS] Pipeline Ingestion Selesai!")
    print(f"- Sumber Data      : {report['source_name']}")
    print(f"- Path Raw Storage : {report['raw_storage_path']}")
    print(f"- Total Diproses   : {report['total_fetched']}")
    print(f"- Berhasil (Valid) : {report['total_valid']}")
    print(f"- Gagal (Invalid)  : {report['total_invalid']}")
    
    # KITA SAMBUNGKAN DATA VALID KE KODE DB + EMBEDDING KITA DI SINI!
    if report['valid_records']:
        save_and_embed_records(report['valid_records'])

if __name__ == "__main__":
    test_orchestrator()