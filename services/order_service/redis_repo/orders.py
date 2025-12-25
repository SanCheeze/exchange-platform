# service/order_service/redis_repo/orders.py

import json
from domain.order_status import OrderStatus


async def cache_order(redis, order_id: str, order: dict, ttl: int):
    await redis.set(f"order:{order_id}", json.dumps(order), ex=ttl)


async def get_cached_order(redis, order_id: str):
    raw = await redis.get(f"order:{order_id}")
    return json.loads(raw) if raw else None
