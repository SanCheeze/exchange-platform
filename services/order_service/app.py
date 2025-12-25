from aiohttp import web
from handlers.api import create_order, get_order
from settings import REDIS_HOST, REDIS_PORT
import redis.asyncio as redis

from kafka_worker import process_outbox


async def init_app():
    app = web.Application()
    app["redis"] = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    app.add_routes([
        web.post("/orders", create_order),
        web.get("/orders/{order_id}", get_order),
    ])

    app.on_startup.append(process_outbox)

    return app

if __name__ == "__main__":
    web.run_app(init_app(), host="0.0.0.0", port=8081)
