import aiohttp
from decimal import Decimal
from models import Rate, ProviderResult
from utils.time import utc_now_iso


async def fetch(base: str, quotes: list[str]) -> ProviderResult:
    try:
        # пример — заглушка
        rates = []
        for q in quotes:
            rates.append(
                Rate(
                    base=base,
                    quote=q,
                    rate=Decimal("1.0"),
                    source="fx",
                    updated_at=utc_now_iso(),
                )
            )

        return ProviderResult(ok=True, rates=rates)

    except Exception as e:
        return ProviderResult(ok=False, rates=[], error=str(e))
