# services/order_service/logic/orders.py

import json
import uuid
from aiohttp import web
import redis.asyncio as redis
from decimal import Decimal, ROUND_DOWN
from datetime import datetime, timezone

from database.pg import init_pg
from database.orders import insert_order, confirm_order_with_outbox
from domain.order_status import OrderStatus

from redis_repo.orders import cache_order, get_cached_order
from redis_repo.quotes import get_quote

from settings import (
    REDIS_HOST,
    REDIS_PORT,
    DATABASE_URI,
    ORDER_TTL_SECONDS,
)


# =====================
# REDIS
# =====================
async def init_redis(app: web.Application):
    app["redis"] = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
    )


async def close_redis(app: web.Application):
    redis_conn = app.get("redis")
    if redis_conn:
        await redis_conn.aclose()


# =====================
# DATABASE
# =====================
async def init_database(app: web.Application):
    await init_pg(DATABASE_URI)


# =====================
# HEALTHCHECK
# =====================
async def healthcheck(request: web.Request):
    try:
        await request.app["redis"].ping()
        return web.json_response({"status": "ok"})
    except Exception as e:
        return web.json_response(
            {"status": "error", "details": str(e)},
            status=500,
        )

# =====================
# CREATE ORDER
# =====================
async def create_order(request: web.Request):
    data = await request.json()

    quote_id = data.get("quote_id")
    client_id = data.get("client_id")
    idem_key = data.get("idempotency_key")

    if not quote_id:
        return web.json_response({"error": "QUOTE_ID_REQUIRED"}, status=400)

    r = request.app["redis"]

    # =====================
    # IDEMPOTENCY
    # =====================
    if idem_key:
        existing_order = await get_cached_order(r, f"idem:{idem_key}")
        if existing_order:
            return web.json_response(existing_order, status=200)

    # =====================
    # LOAD QUOTE
    # =====================
    quote = await get_quote(r, quote_id)
    print(f'create_order() --> quote == {quote}')

    if not quote:
        return web.json_response(
            {"error": "QUOTE_EXPIRED_OR_NOT_FOUND"},
            status=409,
        )

    # =====================
    # IDS & TIMESTAMPS
    # =====================
    order_uuid = uuid.uuid4()
    order_id = f"o_{order_uuid.hex[:12]}"
    ts = datetime.now(timezone.utc)

    # =====================
    # DECIMAL NORMALIZATION
    # =====================
    amount_in = Decimal(str(quote["amount_in"])).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    amount_out = Decimal(str(quote["amount_out"])).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    rate = Decimal(str(quote["rate"])).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)
    commission = Decimal(str(quote["commission"])).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)

    # =====================
    # DB ORDER MODEL
    # =====================
    order = {
        "id": order_uuid,
        "order_id": order_id,
        "status": OrderStatus.CREATED,
        "quote_id": quote_id,
        "pair": f"{quote['from']}_{quote['to']}",
        "amount_in": amount_in,
        "amount_out": amount_out,
        "rate": rate,
        "commission": commission,
        "client_id": client_id,
        "session_id": quote["session_id"],
        "created_at": ts,
        "updated_at": ts,
    }

    # =====================
    # REDIS / API PAYLOAD
    # =====================
    redis_payload = {
        **order,
        "id": str(order_uuid),
        "created_at": ts.isoformat(),
        "updated_at": ts.isoformat(),
        "amount_in": float(amount_in),
        "amount_out": float(amount_out),
        "rate": float(rate),
        "commission": float(commission),
    }

    # =====================
    # REDIS TRANSACTION
    # =====================
    async with r.pipeline(transaction=True) as pipe:
        await cache_order(pipe, order_id, redis_payload, ORDER_TTL_SECONDS)
        pipe.delete(f"quote:{quote_id}")

        if idem_key:
            pipe.set(
                f"idem:{idem_key}",
                order_id,
                ex=3600,
            )

        await pipe.execute()

    # =====================
    # DATABASE
    # =====================
    await insert_order(order)

    return web.json_response(redis_payload, status=201)


# =====================
# CONFIRM ORDER
# =====================
async def confirm_order(request: web.Request):
    order_id = request.match_info["order_id"]

    r = request.app["redis"]
    order = await get_cached_order(r, order_id)

    # 1️⃣ TTL → Redis источник правды
    if not order:
        return web.json_response(
            {"error": "ORDER_EXPIRED"},
            status=409,
        )

    # 2️⃣ Идемпотентность
    if order["status"] == OrderStatus.CONFIRMED:
        return web.json_response(order, status=200)

    # 3️⃣ Формируем событие
    ts = datetime.now(timezone.utc)

    event_payload = {
        "order_id": order_id,
        "pair": order["pair"],
        "amount_in": str(order["amount_in"]),
        "amount_out": str(order["amount_out"]),
        "rate": str(order["rate"]),
        "confirmed_at": ts.isoformat(),
    }

    # 4️⃣ Транзакция БД + outbox
    success = await confirm_order_with_outbox(order_id, event_payload)

    if not success:
        return web.json_response(order, status=200)

    # 5️⃣ Обновляем Redis
    order["status"] = OrderStatus.CONFIRMED
    order["updated_at"] = ts.isoformat()

    await cache_order(r, order_id, order, ORDER_TTL_SECONDS)

    return web.json_response(order, status=200)
