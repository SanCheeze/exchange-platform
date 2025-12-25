# services/pricing_service/app.py

import asyncio
from aiohttp import web
import redis.asyncio as redis

from fetch import fetch_loop
from settings import REDIS_HOST, REDIS_PORT


async def start_fetch_loop(app: web.Application):
    app["fetch_task"] = asyncio.create_task(
        fetch_loop(app["redis"])
    )


async def stop_fetch_loop(app: web.Application):
    task = app.get("fetch_task")
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


async def init_app():
    app = web.Application()

    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
    )
    app["redis"] = redis_client

    app.on_startup.append(start_fetch_loop)
    app.on_cleanup.append(stop_fetch_loop)

    return app


if __name__ == "__main__":
    web.run_app(init_app(), port=8080)
