import asyncio
import redis.asyncio as redis

from config import (
    REDIS_HOST,
    REDIS_PORT,
    UPDATE_INTERVAL,
    BASE_CURRENCY,
    TARGET_CURRENCIES,
)
from providers.fx import fetch_fx_rates
from redis_repo.rates import save_rate


async def update_rates(redis_client: redis.Redis):
    for base in BASE_CURRENCIES:
        symbols = [c for c in TARGET_CURRENCIES if c != base]
        if not symbols:
            continue

        rates = await fetch_fx_rates(base, symbols)

        for rate in rates:
            await save_rate(redis_client, rate)
            print(f"[FX] {rate.base}->{rate.quote} = {rate.rate}")


async def main():
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
    )

    print("Pricing service started")

    while True:
        try:
            await update_rates(redis_client)
        except Exception as e:
            print("Error updating rates:", e)

        await asyncio.sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
