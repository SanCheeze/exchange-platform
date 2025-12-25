from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class Rate:
    base: str
    quote: str
    rate: Decimal
    source: str
    updated_at: str


@dataclass
class ProviderResult:
    ok: bool
    rates: list[Rate]
    error: Optional[str] = None
