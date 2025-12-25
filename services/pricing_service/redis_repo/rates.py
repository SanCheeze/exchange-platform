# services/pricing_service/redis_repo/rates.py

import json


async def save_rate(redis, base, quote, price, source=None, updated_at=None, ttl=None):
    key = f"rate:{base}_{quote}"
    payload = {
        "base": base,
        "quote": quote,
        "rate": str(price),
        "source": source,
        "updated_at": updated_at,
    }
    if ttl:
        await redis.set(key, json.dumps(payload), ex=ttl)
    else:
        await redis.set(key, json.dumps(payload))

async def get_rate(redis, base, quote):
    key = f"rate:{base}_{quote}"
    raw = await redis.get(key)
    if not raw:
        return None
    data = json.loads(raw)
    return float(data["rate"])
