from redis.asyncio import Redis


async def get_rate(redis: Redis, from_currency: str, to_currency: str) -> float | None:
    key = f"{from_currency}_{to_currency}"
    rate = await redis.get(key)
    return float(rate) if rate is not None else None
