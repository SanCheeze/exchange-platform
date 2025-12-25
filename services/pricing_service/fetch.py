import asyncio
from providers import binance, fx, fallback
from redis_repo.rates import save_rate, get_all_rates
from settings import *
from utils.time import utc_now_iso


async def fetch_loop(redis):
    while True:
        all_rates = []

        binance_res = await binance.fetch(CRYPTO_SYMBOLS)
        fx_res = await fx.fetch(FIAT_BASE, FIAT_QUOTES)

        if binance_res.ok:
            all_rates.extend(binance_res.rates)
        else:
            print("[WARN] binance down:", binance_res.error)

        if fx_res.ok:
            all_rates.extend(fx_res.rates)
        else:
            print("[WARN] fx down:", fx_res.error)

        if not all_rates:
            print("[CRITICAL] all providers down, using last known")
            all_rates = await get_all_rates(redis)

        for rate in all_rates:
            await save_rate(redis, rate)

        await asyncio.sleep(FETCH_INTERVAL_SECONDS)
