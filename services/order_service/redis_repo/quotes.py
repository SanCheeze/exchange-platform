import json

async def get_quote(redis, quote_id: str):
    raw = await redis.get(f"quote:{quote_id}")
    return json.loads(raw) if raw else None

async def save_quote(redis, quote_id: str, quote: dict):
    await redis.set(f"quote:{quote_id}", json.dumps(quote))
