import aiohttp
import json
from datetime import datetime, timezone


BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"


async def fetch_binance_rates(symbols: list[str]) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(BINANCE_URL) as resp:
            data = await resp.json()

    result = {}
    ts = datetime.now(timezone.utc).isoformat()

    for item in data:
        if item["symbol"] in symbols:
            base = item["symbol"][:-4]
            quote = item["symbol"][-4:]
            pair = f"{base}_{quote}"

            result[pair] = json.dumps({
                "rate": item["price"],
                "source": "binance",
                "updated_at": ts,
            })

    return result
