# services/pricing_service/app.py

import asyncio
from aiohttp import web
import redis.asyncio as redis

from providers.binance_ws import listen_binance_ws
from settings import REDIS_HOST, REDIS_PORT


async def start_binance_ws(app):
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
    )

    app["redis"] = redis_client
    app["binance_task"] = asyncio.create_task(
        listen_binance_ws(redis_client)
    )


async def stop_binance_ws(app):
    task = app.get("binance_task")
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


async def init_app():
    app = web.Application()
    app.on_startup.append(start_binance_ws)
    app.on_cleanup.append(stop_binance_ws)
    return app


if __name__ == "__main__":
    web.run_app(init_app(), port=8080)
