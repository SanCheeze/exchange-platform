import json


async def save_rate(redis, rate, ttl):
    key = f"rate:{rate.base}_{rate.quote}"
    await redis.set(key, json.dumps({
        "base": rate.base,
        "quote": rate.quote,
        "rate": str(rate.rate),
        "source": rate.source,
        "updated_at": rate.updated_at,
    }), ex=ttl)


async def get_rate(redis, base: str, quote: str):
    key = f"rate:{base}_{quote}"
    raw = await redis.get(key)
    if not raw:
        return None
    data = json.loads(raw)
    return float(data["rate"])


async def get_all_rates(redis):
    keys = await redis.keys("rate:*")
    rates = []
    for key in keys:
        raw = await redis.get(key)
        rates.append(json.loads(raw))
    return rates
