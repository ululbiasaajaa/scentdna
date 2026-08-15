from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from src.models import CanonicalRecord

class DataNormalizer:
    """
    Bertanggung jawab mentransformasi intermediate record dari adapter 
    menjadi CanonicalRecord yang bersih dan siap divalidasi.
    """

    def clean_html_to_text(self, html_content: str) -> str:
        """
        Membersihkan tag HTML, entity, dan merapikan spasi/whitespace berlebih.
        """
        if not html_content:
            return ""
        
        # Gunakan BeautifulSoup untuk membuang tag HTML
        soup = BeautifulSoup(html_content, "html.parser")
        clean_text = soup.get_text(separator=" ")
        
        # Normalisasi spasi berlebih
        return " ".join(clean_text.split())

    def normalize_price(self, price_raw: Any) -> Optional[float]:
        """
        Mengonversi harga mentah ke tipe float jika memungkinkan.
        """
        if price_raw is None:
            return None
        try:
            return float(price_raw)
        except (ValueError, TypeError):
            return None

    def normalize_availability(self, availability_raw: Any) -> Optional[bool]:
        """
        Menangani Tri-state boolean:
        - True jika bernilai True
        - False jika bernilai False
        - None jika datanya tidak diketahui/missing
        """
        if availability_raw is True:
            return True
        if availability_raw is False:
            return False
        return None

    def normalize_record(self, adapted_item: Dict[str, Any]) -> CanonicalRecord:
        """
        Menerima record intermediate, membersihkan teks, merakit searchable_text,
        dan mengembalikan CanonicalRecord instance.
        """
        source_name = adapted_item.get("source_name", "")
        source_id = adapted_item.get("source_id", "")
        source_url = adapted_item.get("source_url", "")
        product_name = adapted_item.get("product_name", "").strip()
        
        # Bersihkan HTML dari body_html
        raw_html = adapted_item.get("raw_body_html", "")
        cleaned_description = self.clean_html_to_text(raw_html)

        # Rancang searchable_text gabungan (Nama produk + deskripsi bersih)
        # Ini adalah sumber utama Vector Embedding nantinya.
        searchable_text = f"{product_name}. {cleaned_description}".strip()

        # Normalisasi atribut pendukung
        price_amount = self.normalize_price(adapted_item.get("price_raw"))
        is_available = self.normalize_availability(adapted_item.get("availability_raw"))
        image_url = adapted_item.get("image_url")

        return CanonicalRecord(
            source_name=source_name,
            source_id=source_id,
            source_url=source_url,
            product_name=product_name,
            searchable_text=searchable_text,
            price_amount=price_amount,
            is_available=is_available,
            image_url=image_url
            # top_notes, middle_notes, base_notes otomatis terisi default empty list []
        )