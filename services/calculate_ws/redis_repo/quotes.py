import json
from redis.asyncio import Redis


QUOTE_TTL_SECONDS = 15


async def save_quote(
    redis: Redis,
    quote_id: str,
    quote_data: dict
) -> None:
    key = f"quote:{quote_id}"
    await redis.set(
        key,
        json.dumps(quote_data),
        ex=QUOTE_TTL_SECONDS
    )
