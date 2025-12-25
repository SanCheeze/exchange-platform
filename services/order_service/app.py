import os
import json
import uuid
from decimal import Decimal, ROUND_DOWN
from datetime import datetime, timezone

import asyncio
from aiohttp import web
import redis.asyncio as redis

from database.pg import init_pg
from database.orders import insert_order, get_order, update_order_status, confirm_order_with_outbox
from domain.order_status import OrderStatus
from kafka_worker import process_outbox

from dotenv import load_dotenv
load_dotenv()


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://exchange:exchange@localhost:5432/exchange")

SERVICE_NAME = "order_service"
ORDER_TTL_SECONDS = 60


# =====================
# REDIS
# =====================
async def init_redis(app: web.Application):
    app["redis"] = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
    )


async def init_database(app: web.Application):
    await init_pg(DATABASE_URI)


async def close_redis(app: web.Application):
    redis_conn = app.get("redis")
    if redis_conn:
        await redis_conn.aclose()


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

    # Idempotency
    if idem_key:
        idem_key_redis = f"idem:{idem_key}"
        existing_order_id = await r.get(idem_key_redis)
        if existing_order_id:
            order_raw = await r.get(f"order:{existing_order_id}")
            if order_raw:
                return web.json_response(json.loads(order_raw))

    # Load quote
    quote_key = f"quote:{quote_id}"
    quote_raw = await r.get(quote_key)
    if not quote_raw:
        return web.json_response({"error": "QUOTE_EXPIRED_OR_NOT_FOUND"}, status=409)

    quote = json.loads(quote_raw)
    print(f'create_order() --> quote -->\n{quote}')

    # Создаём UUID и timestamp
    order_uuid = uuid.uuid4()                # UUID для БД
    order_id = f"o_{order_uuid.hex[:12]}"    # короткий для API
    ts = datetime.now(timezone.utc)          # datetime для БД и Redis

    # Преобразуем числа в Decimal с нужной точностью для БД
    amount_in = Decimal(str(quote["amount_in"])).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    amount_out = Decimal(str(quote["amount_out"])).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    rate = Decimal(str(quote["rate"])).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)
    commission = Decimal(str(quote["commission"])).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)

    # Базовая структура заказа для БД
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

    # Для Redis/API сериализуем datetime и UUID, а Decimal -> float
    redis_payload = {
        **order,
        "id": str(order["id"]),
        "created_at": ts.isoformat(),
        "updated_at": ts.isoformat(),
        "amount_in": float(amount_in),
        "amount_out": float(amount_out),
        "rate": float(rate),
        "commission": float(commission),
    }

    # Сохраняем в Redis
    async with r.pipeline(transaction=True) as pipe:
        pipe.set(f"order:{order_id}", json.dumps(redis_payload), ex=ORDER_TTL_SECONDS)
        pipe.delete(quote_key)
        if idem_key:
            pipe.set(f"idem:{idem_key}", order_id, ex=3600)
        await pipe.execute()

    # Сохраняем в БД
    await insert_order(order)

    return web.json_response(redis_payload, status=201)


# =====================
# CONFIRM ORDER
# =====================
async def confirm_order(request: web.Request):
    order_id = request.match_info["order_id"]

    r = request.app["redis"]
    redis_key = f"order:{order_id}"

    redis_raw = await r.get(redis_key)

    # 1️⃣ TTL → Redis источник правды
    if not redis_raw:
        return web.json_response(
            {"error": "ORDER_EXPIRED"},
            status=409,
        )

    redis_order = json.loads(redis_raw)

    # 2️⃣ Идемпотентность
    if redis_order["status"] == OrderStatus.CONFIRMED:
        return web.json_response(redis_order, status=200)

    # 3️⃣ Формируем событие
    ts = datetime.now(timezone.utc)

    event_payload = {
        "order_id": order_id,
        "pair": redis_order["pair"],
        "amount_in": str(redis_order["amount_in"]),
        "amount_out": str(redis_order["amount_out"]),
        "rate": str(redis_order["rate"]),
        "confirmed_at": ts.isoformat(),
    }

    # 4️⃣ Транзакция БД + outbox
    success = await confirm_order_with_outbox(order_id, event_payload)

    if not success:
        # заказ уже был подтверждён или не в CREATED
        return web.json_response(redis_order, status=200)

    # 5️⃣ Обновляем Redis
    redis_order["status"] = OrderStatus.CONFIRMED
    redis_order["updated_at"] = ts.isoformat()

    await r.set(
        redis_key,
        json.dumps(redis_order),
        ex=ORDER_TTL_SECONDS,
    )

    return web.json_response(redis_order, status=200)


# =====================
# APP FACTORY
# =====================
async def create_app():
    app = web.Application()

    app.router.add_get("/health", healthcheck)
    app.router.add_post("/orders", create_order)
    app.router.add_post("/orders/{order_id}/confirm", confirm_order)

    app.on_startup.append(init_redis)
    app.on_startup.append(init_database)
    app.on_startup.append(process_outbox)

    app.on_cleanup.append(close_redis)

    return app


# =====================
# ENTRYPOINT
# =====================
def main():
    web.run_app(
        create_app(),
        host="0.0.0.0",
        port=8082,
    )


if __name__ == "__main__":
    main()
