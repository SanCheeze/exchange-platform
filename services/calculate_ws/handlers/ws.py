import json
from aiohttp import web, WSMsgType

from utils.ids import generate_session_id
from services.quote_engine import QuoteEngine


async def handle_ws(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    app = request.app
    app["websockets"].add(ws)

    session_id = generate_session_id()
    quote_engine = QuoteEngine(app["redis"])

    await ws.send_json({
        "type": "session_init",
        "session_id": session_id,
    })

    try:
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                continue

            try:
                data = json.loads(msg.data)
            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "error": "invalid json"})
                continue

            if data.get("action") != "get_quote":
                await ws.send_json({"type": "error", "error": "unknown action"})
                continue

            try:
                result = await quote_engine.get_quote(
                    session_id=session_id,
                    from_currency=data["from"],
                    to_currency=data["to"],
                    amount=float(data["amount"]),
                )
            except (KeyError, ValueError) as e:
                await ws.send_json({"type": "error", "error": str(e)})
                continue

            await ws.send_json({
                "type": "quote",
                **result,
            })

    finally:
        app["websockets"].discard(ws)
        await ws.close()

    return ws
