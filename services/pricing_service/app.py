# services/pricing_service/app.py

import asyncio
from aiohttp import web
import redis.asyncio as redis
from fetch import start_periodic_fetch
from settings import REDIS_HOST, REDIS_PORT, FETCH_INTERVAL

async def init_app():
    app = web.Application()
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    app["redis"] = redis_client

    # start fetch loop
    app.on_startup.append(lambda app: asyncio.create_task(start_periodic_fetch(redis_client, FETCH_INTERVAL)))

    return app

if __name__ == "__main__":
    web.run_app(init_app(), port=8080)
