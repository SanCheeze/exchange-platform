import uuid
from typing import Optional

from settings import ORDER_TTL_SECONDS, IDEMPOTENCY_TTL_SECONDS
from domain.order_status import OrderStatus
from redis_repo.quotes import get_quote, save_quote
from redis_repo.orders import cache_order, get_cached_order
from database.orders import insert_order
from utils.time import utc_now_iso


def create_order_payload(quote: dict, client_id: str, session_id: str) -> dict:
    ts = utc_now_iso()
    order_uuid = uuid.uuid4()
    order_id = f"o_{order_uuid.hex[:12]}"

    return {
        "id": order_uuid.hex,
        "order_id": order_id,
        "status": OrderStatus.CREATED,
        "quote_id": quote["quote_id"],
        "pair": f"{quote['from']}_{quote['to']}",
        "amount_in": quote["amount_in"],
        "amount_out": quote["amount_out"],
        "rate": quote["rate"],
        "commission": quote["commission"],
        "client_id": client_id,
        "session_id": session_id,
        "created_at": ts,
        "updated_at": ts,
    }

async def create_order_logic(redis, data: dict) -> dict:
    quote_id = data.get("quote_id")
    client_id = data.get("client_id")
    idem_key = data.get("idempotency_key")

    # idempotency
    if idem_key:
        exist = await get_cached_order(redis, idem_key)
        if exist:
            return exist

    quote = await get_quote(redis, quote_id)
    if not quote:
        raise ValueError("QUOTE_EXPIRED_OR_NOT_FOUND")

    order = create_order_payload(quote, client_id, quote["session_id"])

    # cache order
    await cache_order(redis, order["order_id"], order, ORDER_TTL_SECONDS)

    # cache idem key
    if idem_key:
        await redis.set(f"idem:{idem_key}", order["order_id"], ex=IDEMPOTENCY_TTL_SECONDS)

    # db save
    await insert_order(order)

    return order
