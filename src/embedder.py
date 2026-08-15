import os
import gc
import hashlib
import torch
from typing import List, Optional

# Batasi PyTorch thread pool di level environment & runtime
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

torch.set_num_threads(1)
torch.set_num_interop_threads(1)

from sentence_transformers import SentenceTransformer

class TextEmbedder:
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self._model_name = model_name
        self._model: Optional[SentenceTransformer] = None

    def _load_model(self) -> SentenceTransformer:
        if self._model is None:
            torch.set_num_threads(1)
            torch.set_num_interop_threads(1)
            self._model = SentenceTransformer(self._model_name)
            self._model.eval()
        return self._model

    @staticmethod
    def compute_hash(text: str) -> str:
        """Menghitung SHA-256 hash dari searchable_text untuk change-detection."""
        if not text:
            return ""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 1) -> List[List[float]]:
        """Meng-generate L2-normalized vector embeddings dalam bentuk batch dengan memory optimization."""
        if not texts:
            return []
        
        model = self._load_model()
        torch.set_num_threads(1)
        
        # P2: Bungkus dengan no_grad & paksa batch_size minimal untuk hemat RAM
        with torch.no_grad():
            embeddings = model.encode(
                texts, 
                batch_size=batch_size, 
                normalize_embeddings=True, 
                show_progress_bar=False
            )
        
        result = [emb.tolist() for emb in embeddings]
        
        # Bersihkan referensi memori temporary
        del embeddings
        gc.collect()
        
        return result