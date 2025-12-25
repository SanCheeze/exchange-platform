# services/pricing_service/providers/fallback.py
import aiohttp
from decimal import Decimal
from typing import List
from utils.time import utc_now_iso
from models.rate import Rate

BASE_URL = "https://api.exchangerate.host/latest"

async def get_rates(base_currency: str, symbols: list[str]) -> List[Rate]:
    """
    Фолбэк-провайдер курсов через exchangerate.host.
    """
    params = {
        "base": base_currency,
        "symbols": ",".join(symbols),
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(BASE_URL, params=params, timeout=5) as resp:
                if resp.status != 200:
                    print(f"[Fallback] API returned status {resp.status}")
                    return []

                data = await resp.json()
                rates = []
                for quote, value in data.get("rates", {}).items():
                    rates.append(
                        Rate(
                            base=base_currency,
                            quote=quote,
                            rate=Decimal(str(value)),
                            source="fallback",
                            updated_at=utc_now_iso(),
                        )
                    )
                return rates
        except Exception as e:
            print(f"[Fallback] Error fetching rates: {e}")
            return []
