from aiohttp import web
import redis.asyncio as redis

from handlers.ws import handle_ws
from settings import REDIS_HOST, REDIS_PORT


async def healthcheck(request: web.Request):
    try:
        await request.app["redis"].ping()
    except Exception:
        return web.json_response({"status": "unhealthy"}, status=503)

    return web.json_response({"status": "ok"})


async def on_shutdown(app: web.Application):
    for ws in set(app["websockets"]):
        await ws.close(code=1001, message="Server shutdown")
    await app["redis"].aclose()


async def init_app():
    app = web.Application()

    app["redis"] = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        max_connections=20,
    )

    app["websockets"] = set()
    app.on_shutdown.append(on_shutdown)

    app.add_routes([
        web.get("/ws", handle_ws),
        web.get("/health", healthcheck),
    ])

    return app


if __name__ == "__main__":
    web.run_app(init_app(), port=8080)
