import aiohttp
import json
from datetime import datetime, timezone


FX_URL = "https://api.frankfurter.app/latest"


async def fetch_fx_rates(base: str, symbols: list[str]) -> dict:
    params = {
        "from": base,
        "to": ",".join(symbols),
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(FX_URL, params=params) as resp:
            data = await resp.json()

    result = {}
    ts = datetime.now(timezone.utc).isoformat()

    for symbol, rate in data["rates"].items():
        pair = f"{base}_{symbol}"
        result[pair] = json.dumps({
            "rate": str(rate),
            "source": "frankfurter",
            "updated_at": ts,
        })

    return result
