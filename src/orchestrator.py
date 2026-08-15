from typing import List, Dict, Any
from src.config import MYKONOS_PRODUCTS_URL, MYKONOS_SOURCE_NAME
from src.fetcher import HTTPFetcher, save_raw_payload
from src.adapters.mykonos_adapter import MykonosAdapter
from src.normalizer import DataNormalizer
from src.validator import CanonicalValidator
from src.models import CanonicalRecord

class IngestionOrchestrator:
    """
    Konduktor utama Ingestion Pipeline ScentDNA.
    Mengatur alur: Fetch -> Save Raw -> Adapt -> Normalize -> Validate.
    """
    def __init__(self):
        self.fetcher = HTTPFetcher()
        self.adapter = MykonosAdapter()
        self.normalizer = DataNormalizer()
        self.validator = CanonicalValidator()

    def run_mykonos_pipeline(self) -> Dict[str, Any]:
        """
        Menjalankan seluruh pipeline untuk Official Mykonos.
        Mengembalikan laporan ringkasan dan list CanonicalRecord yang valid.
        """
        report = {
            "source_name": MYKONOS_SOURCE_NAME,
            "total_fetched": 0,
            "total_valid": 0,
            "total_invalid": 0,
            "raw_storage_path": None,
            "valid_records": [],
            "errors": []
        }

        # 1. Fetch Data Mentah dari Internet
        raw_data = self.fetcher.fetch_json(MYKONOS_PRODUCTS_URL)
        products_raw = raw_data.get("products", [])
        report["total_fetched"] = len(products_raw)

        # 2. Simpan Raw Payload ke Local Storage (Data Provenance)
        saved_path = save_raw_payload(MYKONOS_SOURCE_NAME, raw_data)
        report["raw_storage_path"] = str(saved_path)

        # 3. Adaptasi Data Mentah ke Intermediate Record
        adapted_items = self.adapter.adapt(raw_data)

        # 4. Normalisasi & Validasi Per Item
        for item in adapted_items:
            # Normalisasi ke CanonicalRecord
            canonical_record = self.normalizer.normalize_record(item)
            
            # Validasi CanonicalRecord
            is_valid, validation_errors = self.validator.validate(canonical_record)

            if is_valid:
                report["total_valid"] += 1
                report["valid_records"].append(canonical_record)
            else:
                report["total_invalid"] += 1
                report["errors"].append({
                    "source_id": canonical_record.source_id,
                    "product_name": canonical_record.product_name,
                    errors: validation_errors
                })

        return report