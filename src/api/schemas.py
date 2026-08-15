from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class SearchRequest(BaseModel):
    query: str = Field(..., description="Teks kueri pencarian parfum bahasa alami", example="parfum yang fresh bersih buat kantor")
    limit: int = Field(default=5, ge=1, le=20, description="Jumlah hasil maksimum (1-20)")
    # --- Filter Baru ---
    min_price: Optional[float] = Field(default=None, ge=0, description="Harga minimum")
    max_price: Optional[float] = Field(default=None, ge=0, description="Harga maksimum")
    brand: Optional[str] = Field(default=None, description="Filter brand")

    @field_validator("query")
    @classmethod
    def validate_query_not_empty(cls, v: str) -> str:
        clean_query = v.strip()
        if not clean_query:
            raise ValueError("Query pencarian tidak boleh kosong atau hanya berisi spasi.")
        return clean_query

class ProductResult(BaseModel):
    product_name: str
    similarity: float
    price: Optional[float] = None
    source_url: str
    top_notes: List[str] = []
    middle_notes: List[str] = []
    base_notes: List[str] = []

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[ProductResult]

class RecommendRequest(BaseModel):
    query: str = Field(..., description="Permintaan konsultasi parfum", example="Rekomendasiin parfum manis vanilla buat kencan malam hari")
    limit: int = Field(default=3, ge=1, le=5, description="Jumlah referensi produk (1-5)")
    # --- Filter Baru ---
    min_price: Optional[float] = Field(default=None, ge=0)
    max_price: Optional[float] = Field(default=None, ge=0)
    brand: Optional[str] = Field(default=None)

    @field_validator("query")
    @classmethod
    def validate_query_not_empty(cls, v: str) -> str:
        clean_query = v.strip()
        if not clean_query:
            raise ValueError("Query tidak boleh kosong.")
        return clean_query

class RecommendResponse(BaseModel):
    query: str
    ai_recommendation: str
    retrieved_products: List[ProductResult]