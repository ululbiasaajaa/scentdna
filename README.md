# ScentDNA

## 1. Overview
ScentDNA adalah *semantic fragrance search & data engine* berbasis Python yang memproses data produk parfum dari berbagai sumber publik, melakukan normalisasi dan validasi data, meng-generate *vector embedding* berbasis model multilingual, serta menyimpannya ke dalam PostgreSQL menggunakan ekstensi `pgvector`. Engine ini memungkinkan pencarian parfum berdasarkan konteks bahasa alami (*semantic similarity search*) menggunakan perhitungan *cosine distance*.

## 2. Core Features
* **Raw Data Ingestion**: Penarikan data mentah JSON dari API publik dan penyimpanannya secara terstruktur di lokal storage.
* **Canonical Data Normalization & Validation**: Pembersihan HTML, parsing harga/ketersediaan, serta validasi skema ketat menggunakan Pydantic.
* **PostgreSQL Persistence**: Penyimpanan data produk canonical ke dalam database relasional.
* **pgvector Embedding Storage**: Penyimpanan vektor embedding 384-dimensi langsung di tabel produk.
* **SHA-256 Change Detection**: Penghitungan SHA-256 hash pada string `searchable_text` untuk mendeteksi perubahan deskripsi produk.
* **Hash-First Embedding Idempotency**: *Pre-check* status hash dan ketersediaan vektor di database sebelum memanggil model AI, memotong pemanggilan model (*inference*) hingga 100% jika data tidak berubah.
* **Batch Embedding**: Pemrosesan vektor secara kolektif (*batch processing*) untuk data baru atau ter-mutasi.
* **Cosine Similarity Search**: Pencarian semantik antarmuka CLI memanfaatkan operator `<=>` dari `pgvector`.
* **Retrieval Evaluation**: Uji skor kemiripan dan pengukuran *Precision@5* berbasis batas ukur (*threshold*).
* **Regression Tests**: Suite pengujian otomatis untuk konsistensi database, mutasi parsial, dan performa pencarian.

## 3. Architecture

```text
Source (Public JSON)
  │
  ▼
Fetcher
  │
  ▼
Adapter (MykonosAdapter)
  │
  ▼
Normalizer (HTML & Price Cleaner)
  │
  ▼
Validator (Pydantic Canonical Schema)
  │
  ▼
Canonical Product Record
  │
  ▼
PostgreSQL (products table)
  ├── Pre-check SHA-256 Hash ──┐
  │                            │
  │ (Data Sama)                │ (Data Baru/Berubah)
  ▼                            ▼
Skip Inference          Text Embedder (SentenceTransformer)
  │                            │
  │ (Preserve Vector)          │ (Generate 384-dim Vector)
  └─────────────┬──────────────┘
                ▼
  UPSERT (COALESCE Vector) ──► pgvector Storage
                                      │
                                      ▼
                           Semantic Search CLI (<=>)