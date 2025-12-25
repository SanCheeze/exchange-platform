import asyncio
from aiohttp import web
import redis.asyncio as redis
from fetch import fetch_loop


async def init_app():
    app = web.Application()

    redis_client = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True,
    )

    app["redis"] = redis_client
    app.on_startup.append(lambda app: asyncio.create_task(fetch_loop(redis_client)))

    return app


if __name__ == "__main__":
    web.run_app(init_app(), port=8090)
