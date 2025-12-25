import aiohttp
from decimal import Decimal
from datetime import datetime
from models.rate import Rate


FX_URL = "https://api.exchangerate.host/latest"


async def fetch_fx_rates(base: str, symbols: list[str]) -> list[Rate]:
    params = {
        "base": base,
        "symbols": ",".join(symbols),
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(FX_URL, params=params) as resp:
            data = await resp.json()

    rates = []
    for quote, value in data["rates"].items():
        rates.append(
            Rate(
                base=base,
                quote=quote,
                rate=Decimal(str(value)),
                source="fx",
                updated_at=datetime.utcnow(),
            )
        )

    return rates
