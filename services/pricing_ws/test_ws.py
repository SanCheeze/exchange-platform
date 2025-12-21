import asyncio
import json
from aiohttp import ClientSession, WSMsgType


async def test():
    uri = "http://localhost:8080/ws"

    async with ClientSession() as session:
        async with session.ws_connect(uri) as ws:

            # 1️⃣ Получаем session_init
            msg = await ws.receive()
            if msg.type != WSMsgType.TEXT:
                print("Unexpected message type on connect")
                return

            data = json.loads(msg.data)
            print(f"Received: {data}")

            session_id = data.get("session_id")
            if not session_id:
                print("No session_id received")
                return

            # 2️⃣ Отправляем запрос на quote
            message = {
                "action": "get_quote",
                "amount": 100,
                "from": "USD",
                "to": "EUR"
            }

            print(f"Sending: {message}")
            await ws.send_json(message)

            # 3️⃣ Ожидаем ответ quote
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    print(f"Received: {data}")

                    if data.get("type") == "quote":
                        break

                elif msg.type == WSMsgType.ERROR:
                    print(f"WebSocket error: {ws.exception()}")
                    break

            # 4️⃣ Корректно закрываем соединение
            await ws.close()


if __name__ == "__main__":
    asyncio.run(test())
