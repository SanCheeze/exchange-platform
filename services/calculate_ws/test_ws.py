import asyncio
import json
from aiohttp import ClientSession, WSMsgType

WS_URL = "http://localhost:8081/ws"


async def test():
    async with ClientSession() as session:
        async with session.ws_connect(WS_URL) as ws:

            # 1) получаем session_id
            init_msg = await ws.receive()
            if init_msg.type == WSMsgType.TEXT:
                print("INIT:", init_msg.data)
                try:
                    init_data = json.loads(init_msg.data)
                    session_id = init_data.get("session_id")
                except Exception:
                    session_id = None
            else:
                print("Failed to get session_id")
                return

            print("SESSION_ID:", session_id)

            # 2) тестируем прямую пару (USD → USDT)
            message = {
                "action": "get_quote",
                "from": "BTC",
                "to": "USDT",
                "amount": 0.001
            }

            print("\nSENDING direct conversion:", message)
            await ws.send_json(message)

            msg = await ws.receive(timeout=5)
            if msg.type == WSMsgType.TEXT:
                print("RECEIVED:", msg.data)
            else:
                print("FAILED direct conversion")

            # 3) тестируем обратную пару (USDT → BTC)
            message_reverse = {
                "action": "get_quote",
                "from": "USDT",
                "to": "BTC",
                "amount": 50
            }

            print("\nSENDING reverse conversion:", message_reverse)
            await ws.send_json(message_reverse)

            msg2 = await ws.receive(timeout=5)
            if msg2.type == WSMsgType.TEXT:
                print("RECEIVED:", msg2.data)
            else:
                print("FAILED reverse conversion")

            # 4) тестируем некорректную пару
            bad_message = {
                "action": "get_quote",
                "from": "FAKE",
                "to": "AAA",
                "amount": 100
            }

            print("\nSENDING bad conversion:", bad_message)
            await ws.send_json(bad_message)

            bad_msg = await ws.receive(timeout=5)
            if bad_msg.type == WSMsgType.TEXT:
                print("RECEIVED:", bad_msg.data)
            else:
                print("FAILED bad conversion")

            # 5) закрываем WS
            await ws.close()

asyncio.run(test())
