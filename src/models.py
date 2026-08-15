from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class CanonicalRecord:
    source_name: str
    source_id: str
    source_url: str
    product_name: str
    searchable_text: str
    price_amount: Optional[float] = None
    is_available: Optional[bool] = None
    top_notes: List[str] = field(default_factory=list)
    middle_notes: List[str] = field(default_factory=list)
    base_notes: List[str] = field(default_factory=list)
    image_url: Optional[str] = None