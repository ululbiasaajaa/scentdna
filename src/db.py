import psycopg
from typing import Dict, List, Tuple, Optional
from src.config import DATABASE_URL

def init_db():
    """Eksekusi DDL Migration untuk skema products dan pgvector."""
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id BIGSERIAL PRIMARY KEY,
                    source_name VARCHAR(100) NOT NULL,
                    source_id VARCHAR(100) NOT NULL,
                    source_url TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    searchable_text TEXT NOT NULL,
                    price_amount NUMERIC(12, 2) NULL,
                    is_available BOOLEAN NULL,
                    top_notes TEXT[] NULL,
                    middle_notes TEXT[] NULL,
                    base_notes TEXT[] NULL,
                    image_url TEXT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_source_product UNIQUE (source_name, source_id)
                );
            """)
            cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS embedding vector(384);")
            cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS searchable_text_hash VARCHAR(64);")
        conn.commit()

def fetch_existing_hashes(source_name: str, source_ids: List[str]) -> Dict[str, Tuple[Optional[str], bool]]:
    """
    Pre-check DB: Mengambil (searchable_text_hash, has_embedding) berdasarkan source_ids.
    Returns: Dict[source_id, (hash, has_embedding)]
    """
    if not source_ids:
        return {}
    
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT source_id, searchable_text_hash, (embedding IS NOT NULL) AS has_embedding
                FROM products
                WHERE source_name = %s AND source_id = ANY(%s);
            """, (source_name, source_ids))
            rows = cur.fetchall()
            return {row[0]: (row[1], row[2]) for row in rows}

def upsert_canonical_products(records_data: List[dict]):
    """
    UPSERT batch dengan dukungan COALESCE pada embedding.
    Jika embedding bernilai None, maka vector lama di DB tidak ditimpa.
    """
    query = """
    INSERT INTO products (
        source_name, source_id, source_url, product_name, searchable_text,
        price_amount, is_available, top_notes, middle_notes, base_notes, image_url,
        searchable_text_hash, embedding, updated_at
    ) VALUES (
        %(source_name)s, %(source_id)s, %(source_url)s, %(product_name)s, %(searchable_text)s,
        %(price_amount)s, %(is_available)s, %(top_notes)s, %(middle_notes)s, %(base_notes)s, %(image_url)s,
        %(searchable_text_hash)s, %(embedding)s, CURRENT_TIMESTAMP
    )
    ON CONFLICT (source_name, source_id)
    DO UPDATE SET
        source_url = EXCLUDED.source_url,
        product_name = EXCLUDED.product_name,
        searchable_text = EXCLUDED.searchable_text,
        price_amount = EXCLUDED.price_amount,
        is_available = EXCLUDED.is_available,
        top_notes = EXCLUDED.top_notes,
        middle_notes = EXCLUDED.middle_notes,
        base_notes = EXCLUDED.base_notes,
        image_url = EXCLUDED.image_url,
        searchable_text_hash = EXCLUDED.searchable_text_hash,
        embedding = COALESCE(EXCLUDED.embedding, products.embedding),
        updated_at = CURRENT_TIMESTAMP;
    """
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.executemany(query, records_data)
        conn.commit()