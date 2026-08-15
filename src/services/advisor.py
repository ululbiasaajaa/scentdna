import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.search import ScentSearchEngine

load_dotenv()
logger = logging.getLogger("scentdna_advisor")

class FragranceAdvisor:
    def __init__(self):
        self.search_engine = ScentSearchEngine()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY tidak ditemukan di environment variables!")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
            
        self.model_name = "gemini-3.5-flash"

    def recommend_perfume(
        self, 
        query: str, 
        top_k: int = 3, 
        min_price: Optional[float] = None, 
        max_price: Optional[float] = None, 
        brand: Optional[str] = None
    ) -> Dict[str, Any]:
        
        # Teruskan parameter filter ke ScentSearchEngine
        retrieved_items = self.search_engine.search_similar_perfumes(
            query_text=query, 
            top_k=top_k, 
            min_price=min_price, 
            max_price=max_price, 
            brand=brand
        )
        
        if not retrieved_items:
            return {
                "query": query,
                "ai_recommendation": "Maaf, tidak ditemukan parfum yang sesuai dengan kriteria dan filter harga/brand Anda.",
                "retrieved_products": []
            }

        context_lines = []
        for idx, item in enumerate(retrieved_items, start=1):
            context_lines.append(
                f"Product {idx}:\n"
                f"- Name: {item['product_name']}\n"
                f"- Price: IDR {item.get('price', 'N/A')}\n"
                f"- Similarity Score: {item['score'] * 100:.1f}%\n"
                f"- URL: {item['source_url']}\n"
            )
        context_str = "\n".join(context_lines)

        if not self.client:
            return {
                "query": query,
                "ai_recommendation": "[Fallback Mode] Gemini API key belum dikonfigurasi.",
                "retrieved_products": retrieved_items
            }

        system_instruction = (
            "Anda adalah Fragrance AI Consultant yang ramah, profesional, dan ahli dalam dunia parfum. "
            "Berikan rekomendasi berdasarkan HANYA pada DATA PRODUK yang disediakan.\n"
            "ATURAN: Jangan merekomendasikan produk di luar daftar."
        )

        prompt = (
            f"Kriteria pengguna: \"{query}\"\n\n"
            f"Data produk resmi (sudah disaring sesuai kriteria):\n{context_str}\n\n"
            "Berikan ulasan dan rekomendasi konsultasi yang menarik berdasarkan data di atas!"
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                    max_output_tokens=500
                )
            )
            ai_text = response.text
        except Exception as e:
            logger.error(f"Error saat memanggil Gemini API: {str(e)}")
            ai_text = f"Maaf, terjadi kendala koneksi AI: {str(e)}"

        return {
            "query": query,
            "ai_recommendation": ai_text,
            "retrieved_products": retrieved_items
        }