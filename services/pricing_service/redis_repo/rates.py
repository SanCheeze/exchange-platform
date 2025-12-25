import json
from redis.asyncio import Redis
from models.rate import Rate


def redis_key(base: str, quote: str) -> str:
    return f"rate:{base}_{quote}"


async def save_rate(redis: Redis, rate: Rate):
    key = redis_key(rate.base, rate.quote)

    payload = {
        "rate": str(rate.rate),
        "source": rate.source,
        "updated_at": rate.updated_at,
    }

    await redis.set(key, json.dumps(payload))
