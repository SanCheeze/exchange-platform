import asyncio
from aiohttp import ClientSession, WSMsgType
import json

async def test():
    uri = "http://localhost:8080/ws"  # адрес твоего WebSocket сервиса
    async with ClientSession() as session:
        async with session.ws_connect(uri) as ws:
            
            # Тестовое сообщение
            message = {
                "action": "get_quote",
                "amount": 100,
                "from": "USD",
                "to": "EUR"
            }
            print(f"Sending: {message}")
            await ws.send_json(message)

            # Ожидаем ответ
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    print(f"Received: {msg.data}")
                    break  # завершаем после одного ответа
                elif msg.type == WSMsgType.ERROR:
                    print(f"WebSocket error: {ws.exception()}")
                    break

asyncio.run(test())
