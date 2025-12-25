import aiohttp
from decimal import Decimal
from models import Rate, ProviderResult
from utils.time import utc_now_iso

BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"


async def fetch(symbols: list[str]) -> ProviderResult:
    rates = []

    try:
        async with aiohttp.ClientSession() as session:
            for symbol in symbols:
                async with session.get(BINANCE_URL, params={"symbol": symbol}) as r:
                    data = await r.json()

                    base = symbol[:-4]
                    quote = symbol[-4:]

                    rates.append(
                        Rate(
                            base=base,
                            quote=quote,
                            rate=Decimal(data["price"]),
                            source="binance",
                            updated_at=utc_now_iso(),
                        )
                    )

        return ProviderResult(ok=True, rates=rates)

    except Exception as e:
        return ProviderResult(ok=False, rates=[], error=str(e))
