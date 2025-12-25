import json
from decimal import Decimal
from redis.asyncio import Redis


async def get_rate(redis: Redis, from_currency: str, to_currency: str) -> Decimal | None:
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return Decimal("1")

    async def load(symbol: str) -> Decimal | None:
        raw = await redis.get(f"rate:{symbol}_USDT")
        if not raw:
            return None
        return Decimal(json.loads(raw)["rate"])

    # X -> USDT
    if to_currency == "USDT":
        return await load(from_currency)

    # USDT -> X
    if from_currency == "USDT":
        rate = await load(to_currency)
        return (Decimal("1") / rate) if rate else None

    # X -> Y (через USDT)
    rate_from = await load(from_currency)
    rate_to = await load(to_currency)

    if not rate_from or not rate_to:
        return None

    return rate_from / rate_to
