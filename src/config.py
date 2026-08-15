import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_STORAGE_DIR = BASE_DIR / "storage" / "raw"
os.makedirs(RAW_STORAGE_DIR, exist_ok=True)

MYKONOS_PRODUCTS_URL = "https://officialmykonos.com/products.json"
MYKONOS_SOURCE_NAME = "official_mykonos"

# Database Connection String
DATABASE_URL = "postgresql://scentdna_user:scentdna_password@127.0.0.1:5433/scentdna_db"