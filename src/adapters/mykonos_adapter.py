from typing import Dict, Any, List

class MykonosAdapter:
    """
    Adapter khusus untuk mengurai payload JSON mentah dari Official Mykonos (Shopify)
    dan memetakannya ke struktur intermediate ScentDNA.
    """
    def __init__(self):
        self.source_name = "official_mykonos"

    def adapt(self, raw_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Menerima raw payload dictionary, mengekstrak list produk, 
        dan mengembalikan list record mentah terstruktur.
        """
        products = raw_payload.get("products", [])
        adapted_records = []

        for p in products:
            product_id = str(p.get("id", ""))
            handle = p.get("handle", "")
            source_url = f"https://officialmykonos.com/products/{handle}" if handle else ""
            title = p.get("title", "")
            body_html = p.get("body_html", "")

            # Ambil varian pertama untuk harga dan ketersediaan
            variants = p.get("variants", [])
            price_raw = None
            is_available_raw = None

            if variants:
                first_variant = variants[0]
                price_raw = first_variant.get("price")
                is_available_raw = first_variant.get("available")

            # Ambil gambar pertama jika tersedia
            images = p.get("images", [])
            image_url = images[0].get("src") if images else None

            # Masukkan ke dictionary intermediate
            record = {
                "source_name": self.source_name,
                "source_id": product_id,
                "source_url": source_url,
                "product_name": title,
                "raw_body_html": body_html,
                "price_raw": price_raw,
                "availability_raw": is_available_raw,
                "image_url": image_url
            }
            adapted_records.append(record)

        return adapted_records