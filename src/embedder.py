import hashlib
from typing import List, Optional
from sentence_transformers import SentenceTransformer

class TextEmbedder:
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self._model_name = model_name
        self._model: Optional[SentenceTransformer] = None

    def _load_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self._model_name)
        return self._model

    @staticmethod
    def compute_hash(text: str) -> str:
        """Menghitung SHA-256 hash dari searchable_text untuk change-detection."""
        if not text:
            return ""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Meng-generate L2-normalized vector embeddings dalam bentuk batch."""
        if not texts:
            return []
        
        model = self._load_model()
        embeddings = model.encode(
            texts, 
            batch_size=batch_size, 
            normalize_embeddings=True, 
            show_progress_bar=False
        )
        return [emb.tolist() for emb in embeddings]