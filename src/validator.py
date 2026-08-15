from typing import List, Tuple, Optional
from urllib.parse import urlparse
from src.models import CanonicalRecord

class CanonicalValidator:
    def _is_valid_url(self, url: Optional[str]) -> bool:
        if not url:
            return False
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False

    def validate(self, record: CanonicalRecord) -> Tuple[bool, List[str]]:
        errors = []

        if not record.source_name or not record.source_name.strip():
            errors.append("Field 'source_name' wajib diisi dan tidak boleh kosong.")
        
        if not record.source_id or not record.source_id.strip():
            errors.append("Field 'source_id' wajib diisi dan tidak boleh kosong.")

        if not record.product_name or not record.product_name.strip():
            errors.append("Field 'product_name' wajib diisi dan tidak boleh kosong.")

        if not record.searchable_text or len(record.searchable_text.strip()) < 10:
            errors.append("Field 'searchable_text' wajib diisi dan minimal berisi 10 karakter.")

        if not self._is_valid_url(record.source_url):
            errors.append(f"Field 'source_url' tidak valid: '{record.source_url}'")

        if record.image_url and not self._is_valid_url(record.image_url):
            errors.append(f"Field 'image_url' tidak valid: '{record.image_url}'")

        if record.price_amount is not None and record.price_amount < 0:
            errors.append("Field 'price_amount' tidak boleh bernilai negatif.")

        if record.is_available is not None and not isinstance(record.is_available, bool):
            errors.append("Field 'is_available' harus bertipe boolean atau null.")

        return len(errors) == 0, errors