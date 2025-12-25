# services/pricing_service/binance_ws.py

import asyncio
import json
import aiohttp

from settings import BINANCE_WS_URL, REDIS_RATE_TTL
from redis_repo.rates import save_rate
from utils.normalizer import normalize_symbol
from utils.time import utc_now_iso


async def listen_binance_ws(redis):
    """
    Подключается к Binance WS (!ticker@arr),
    сохраняет все пары BASE/USDT в Redis.
    """

    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(
                    BINANCE_WS_URL,
                    heartbeat=30,
                    timeout=10,
                ) as ws:
                    print("[pricing_service] Connected to Binance WS")

                    async for msg in ws:
                        if msg.type != aiohttp.WSMsgType.TEXT:
                            continue

                        data = json.loads(msg.data)
                        if not isinstance(data, list):
                            continue

                        ts = utc_now_iso()

                        for ticker in data:
                            symbol = ticker.get("s")
                            price = ticker.get("c")

                            if not symbol or not price:
                                continue

                            normalized = normalize_symbol(symbol)
                            if not normalized:
                                continue

                            base, quote = normalized

                            await save_rate(
                                redis=redis,
                                base=base,
                                quote=quote,
                                price=price,
                                source="binance",
                                updated_at=ts,
                                ttl=REDIS_RATE_TTL,
                            )

        except asyncio.CancelledError:
            print("[pricing_service] Binance WS task cancelled")
            break

        except Exception as e:
            print("[pricing_service] Binance WS error:", e)
            # backoff перед реконнектом
            await asyncio.sleep(2)
