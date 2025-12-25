# services/pricing_service/providers/fx.py
import aiohttp
from decimal import Decimal
from typing import List
from models import Rate, ProviderResult
from utils.time import utc_now_iso

BASE_URL = "https://api.frankfurter.app/latest"

async def fetch(base: str, symbols: List[str]) -> ProviderResult:
    """
    FX провайдер без API ключа (использует Frankfurter).
    """
    try:
        params = {
            "base": base,
            "symbols": ",".join(symbols),
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL, params=params) as resp:
                if resp.status != 200:
                    return ProviderResult(False, [], f"status {resp.status}")

                data = await resp.json()

        rates: List[Rate] = []
        for quote, value in data.get("rates", {}).items():
            rates.append(
                Rate(
                    base=base,
                    quote=quote,
                    rate=Decimal(str(value)),
                    source="fx",
                    updated_at=utc_now_iso(),
                )
            )

        return ProviderResult(True, rates)

    except Exception as e:
        return ProviderResult(False, [], str(e))
