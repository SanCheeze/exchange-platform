# services/pricing_service/providers/binance.py
import aiohttp
from decimal import Decimal
from typing import List
from utils.time import utc_now_iso
from models.rate import Rate

BASE_URL = "https://api.binance.com/api/v3/ticker/price"

async def get_rates(symbols: list[str]) -> List[Rate]:
    """
    Получает курсы с Binance.
    Binance использует формат символов: BTCUSDT, EURUSDT и т.д.
    Возвращает список объектов Rate.
    """
    rates: list[Rate] = []

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(BASE_URL, timeout=5) as resp:
                if resp.status != 200:
                    print(f"[Binance] API returned status {resp.status}")
                    return []

                data = await resp.json()
                for item in data:
                    sym = item["symbol"]
                    # фильтруем только интересующие пары
                    if sym in symbols:
                        base = sym[:-4]  # пример: EURUSDT -> EUR
                        quote = sym[-4:]  # USDT
                        rates.append(
                            Rate(
                                base=base,
                                quote=quote,
                                rate=Decimal(item["price"]),
                                source="binance",
                                updated_at=utc_now_iso(),
                            )
                        )
            return rates
        except Exception as e:
            print(f"[Binance] Error fetching rates: {e}")
            return []
