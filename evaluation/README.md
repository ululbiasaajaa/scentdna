# ScentDNA Evaluation Framework

Folder ini berisi dataset *ground truth* dan skrip evaluasi terisolasi untuk mengukur performa Retrieval (Semantic Search), Advanced Filtering, dan RAG (Gemini AI Consultant) pada project ScentDNA.

## Struktur Folder
- `dataset.json`: Kumpulan *evaluation queries*, *expected relevant products* (menggunakan nama produk riil di database), dan parameter *filters* terkait.
- Skrip evaluator (akan datang):
  - `evaluate_retrieval.py`
  - `evaluate_filters.py`
  - `evaluate_rag.py`

## Aturan Dataset
1. Seluruh nama produk di dalam `relevant_products` **wajib** menggunakan string nama produk yang valid dan benar-benar tersimpan di database PostgreSQL.
2. Parameter *filters* dirancang selaras dengan skema request API (`min_price`, `max_price`, `brand`).

## Cara Menjalankan Evaluasi (Preview)
Setelah skrip evaluator selesai dibuat, pengujian dapat dijalankan langsung melalui terminal root project:
```bash
python evaluation/evaluate_retrieval.py
python evaluation/evaluate_filters.py
python evaluation/evaluate_rag.py