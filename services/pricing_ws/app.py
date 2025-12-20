import asyncio
import os
from aiohttp import web, WSMsgType
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

async def handle_ws(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            data = msg.json()
            print(f'app.py << {data}')

            if data.get("action") == "get_quote":
                key = f"{data['from']}_{data['to']}"
                rate = await r.get(key)
                if rate is None:
                    await ws.send_json({"error": f"No rate for {data['from']}->{data['to']}"})
                    continue
                commission = 0.005
                amount = float(data["amount"])
                quote = float(rate) * amount * (1 - commission)

                output = {"amount": amount, "quote": round(quote, 2)}
                await ws.send_json(output)

                print(f'app.py >> {output}')

        elif msg.type == WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())

    await r.aclose()
    return ws

async def init_app():
    app = web.Application()
    app.add_routes([web.get('/ws', handle_ws)])
    return app

if __name__ == '__main__':
    web.run_app(init_app(), port=8080)
