import os
import json
from aiohttp import web, WSMsgType
import redis.asyncio as redis
from dotenv import load_dotenv

from utils.ids import generate_session_id, generate_quote_id
from redis_repo.rates import get_rate
from redis_repo.quotes import save_quote, QUOTE_TTL_SECONDS
from logic.quote import calc_quote, build_quote

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))


# ---------- WebSocket Handler ----------

async def handle_ws(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    app = request.app
    redis_client: redis.Redis = app["redis"]

    # регистрируем WS
    app["websockets"].add(ws)

    session_id = generate_session_id()
    print(f"[WS CONNECT] session_id={session_id}")

    # отправляем session_id клиенту
    await ws.send_json({
        "type": "session_init",
        "session_id": session_id
    })

    try:
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                continue

            data = json.loads(msg.data)
            print(f"[{session_id}] << {data}")

            if data.get("action") != "get_quote":
                await ws.send_json({
                    "type": "error",
                    "error": "unknown action"
                })
                continue

            try:
                amount = float(data["amount"])
                from_currency = data["from"]
                to_currency = data["to"]
            except (KeyError, ValueError):
                await ws.send_json({
                    "type": "error",
                    "error": "invalid payload"
                })
                continue

            rate = await get_rate(redis_client, from_currency, to_currency)
            if rate is None:
                await ws.send_json({
                    "type": "error",
                    "error": f"No rate for {from_currency}->{to_currency}"
                })
                continue

            amount_out = calc_quote(amount, rate)
            quote_id = generate_quote_id()

            quote = build_quote(
                quote_id=quote_id,
                session_id=session_id,
                from_currency=from_currency,
                to_currency=to_currency,
                amount_in=amount,
                rate=rate,
                amount_out=amount_out
            )

            await save_quote(redis_client, quote_id, quote)

            response = {
                "type": "quote",
                "quote_id": quote_id,
                "amount_out": amount_out,
                "expires_in": QUOTE_TTL_SECONDS
            }

            await ws.send_json(response)
            print(f"[{session_id}] >> {response}")

    finally:
        app["websockets"].discard(ws)
        print(f"[WS DISCONNECT] session_id={session_id}")

    return ws


# ---------- Healthcheck ----------

async def healthcheck(request: web.Request):
    redis_client: redis.Redis = request.app["redis"]

    try:
        await redis_client.ping()
    except Exception:
        return web.json_response(
            {"status": "unhealthy", "redis": "down"},
            status=503
        )

    return web.json_response({"status": "ok"}, status=200)


# ---------- Graceful Shutdown ----------

async def on_shutdown(app: web.Application):
    print("Graceful shutdown started...")

    # закрываем все WS соединения
    for ws in set(app["websockets"]):
        await ws.close(code=1001, message="Server shutdown")

    # закрываем Redis pool
    await app["redis"].aclose()

    print("Graceful shutdown completed.")


# ---------- App Factory ----------

async def init_app():
    app = web.Application()

    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        max_connections=20
    )

    app["redis"] = redis_client
    app["websockets"] = set()

    app.on_shutdown.append(on_shutdown)

    app.add_routes([
        web.get("/ws", handle_ws),
        web.get("/health", healthcheck),
    ])

    return app


# ---------- Entrypoint ----------

if __name__ == "__main__":
    web.run_app(init_app(), port=8080)
