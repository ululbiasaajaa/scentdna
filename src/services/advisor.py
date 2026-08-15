import logging
import os
from google import genai
from src.search import ScentSearchEngine

logger = logging.getLogger("scentdna_api")

class FragranceAdvisor:
    def __init__(self, search_engine: ScentSearchEngine):
        """
        Dependency Injection: Menggunakan shared instance ScentSearchEngine yang sudah ada.
        Mencegah pembuatan model SentenceTransformer kedua di memori RAM.
        """
        self.search_engine = search_engine
        
        # Setup Gemini API Client
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY tidak ditemukan di Environment Variables!")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

    def recommend_perfume(self, query: str, top_k: int = 5, min_price: float = None, max_price: float = None, brand: str = None) -> dict:
        retrieved_products = self.search_engine.search_similar_perfumes(
            query_text=query,
            top_k=top_k,
            min_price=min_price,
            max_price=max_price,
            brand=brand
        )

        if not retrieved_products:
            return {
                "query": query,
                "ai_recommendation": "Maaf, tidak ditemukan parfum yang sesuai dengan kriteria filter Anda.",
                "retrieved_products": []
            }

        context_text = "\n".join([
            f"- {p['product_name']} (Similarity: {p['score']:.2f}): Top Notes: {', '.join(p.get('top_notes', []))}, "
            f"Middle Notes: {', '.join(p.get('middle_notes', []))}, Base Notes: {', '.join(p.get('base_notes', []))}"
            for p in retrieved_products
        ])

        prompt = f"""Kamu adalah Fragrance Consultant profesional ScentDNA. 
Berdasarkan kueri pengguna: "{query}"

Berikut adalah daftar parfum yang paling relevan dari database kami:
{context_text}

Berikan rekomendasi dan alasan singkat mengapa parfum-parfum ini cocok dengan kueri pengguna secara elegan dan deskriptif."""

        ai_recommendation = "Rekomendasi AI tidak tersedia."
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                ai_recommendation = response.text
            except Exception as e:
                logger.error(f"Error calling Gemini API: {str(e)}")
                ai_recommendation = "Gagal menghubungi AI Consultant saat ini, berikut adalah hasil pencarian produk teratas."

        return {
            "query": query,
            "ai_recommendation": ai_recommendation,
            "retrieved_products": retrieved_products
        }