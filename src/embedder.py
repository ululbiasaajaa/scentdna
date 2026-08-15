import os
import gc
import hashlib
import torch
from typing import List, Optional

# Set PyTorch thread limit HANYA SEKALI di paling atas file (Module Level)
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

torch.set_num_threads(1)
try:
    torch.set_num_interop_threads(1)
except RuntimeError:
    pass

from sentence_transformers import SentenceTransformer

class TextEmbedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self._model_name = model_name
        self._model: Optional[SentenceTransformer] = None

    def _load_model(self) -> SentenceTransformer:
        if self._model is None:
            # Dihapus set_num_interop_threads dari sini agar tidak memicu RuntimeError
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
        
        # Jalankan inference secara aman dengan no_grad
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