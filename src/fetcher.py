import json
from datetime import datetime
from pathlib import Path
import httpx
from src.config import RAW_STORAGE_DIR

class HTTPFetcher:
    """
    Komponen generic untuk mengambil payload HTTP secara aman 
    tanpa terikat dengan struktur data vendor tertentu.
    """
    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    def fetch_json(self, url: str) -> dict:
        """
        Melakukan GET request ke URL target dan mengembalikan data dalam bentuk dictionary.
        """
        headers = {
            "User-Agent": "ScentDNA-LearningProject/1.0 (Educational AI Portfolio)"
        }
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP Error {e.response.status_code} saat mengakses {url}") from e
        except httpx.RequestError as e:
            raise RuntimeError(f"Network Error saat mengakses {url}: {e}") from e

def save_raw_payload(source_name: str, payload: dict) -> Path:
    """
    Menyimpan raw payload ke Local Storage dengan timestamp 
    untuk menjaga provenance data (bisa diproses ulang kapan saja).
    """
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{source_name}_raw_{timestamp_str}.json"
    file_path = RAW_STORAGE_DIR / file_name

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return file_path