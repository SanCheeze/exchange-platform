import asyncio
import json
import os
import uuid
from aiohttp import web
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

SERVICE_NAME = "order_service"


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
        return web.json_response(
            {"error": "QUOTE_ID_REQUIRED"},
            status=400,
        )

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
        return web.json_response(
            {"error": "QUOTE_EXPIRED_OR_NOT_FOUND"},
            status=409,
        )

    quote = json.loads(quote_raw)
    print(f'create_order() --> quote -->\n{quote}')

    # Create order
    order_id = f"o_{uuid.uuid4().hex[:12]}"
    order = {
        "order_id": order_id,
        "status": "CREATED",
        "quote_id": quote_id,
        "pair": f"{quote['from']}_{quote['to']}",
        "amount_in": quote["amount_in"],
        "amount_out": quote["amount_out"],
        "client_id": client_id,
    }

    async with r.pipeline(transaction=True) as pipe:
        pipe.set(f"order:{order_id}", json.dumps(order))
        pipe.delete(quote_key)

        if idem_key:
            pipe.set(f"idem:{idem_key}", order_id, ex=3600)

        await pipe.execute()

    print(order)

    return web.json_response(order, status=201)


# =====================
# APP FACTORY
# =====================
async def create_app():
    app = web.Application()

    app.router.add_get("/health", healthcheck)
    app.router.add_post("/orders", create_order)

    app.on_startup.append(init_redis)
    app.on_cleanup.append(close_redis)

    return app


# =====================
# ENTRYPOINT
# =====================
def main():
    web.run_app(
        create_app(),
        host="0.0.0.0",
        port=8081,
    )


if __name__ == "__main__":
    main()


