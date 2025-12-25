# service/order_service/redis_repo/quotes.py

import json


async def get_quote(redis, quote_id: str):
    raw = await redis.get(f"quote:{quote_id}")
    return json.loads(raw) if raw else None
