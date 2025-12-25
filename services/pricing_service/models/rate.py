from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Rate:
    base: str
    quote: str
    rate: Decimal
    source: str
    updated_at: datetime
