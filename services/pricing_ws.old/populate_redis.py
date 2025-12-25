import asyncio
import os
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# namespace курсов — такой же, как использует pricing_ws
RATES = {
    "USD_EUR": 0.95,
    "EUR_USD": 1.05,
    "USD_USDT": 1.0,
    "USDT_USD": 1.0,
    "EUR_USDT": 1.02,
    "USDT_EUR": 0.98,
}


async def main():
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        max_connections=5
    )

    try:
        # проверяем соединение
        await redis_client.ping()

        for pair, rate in RATES.items():
            await redis_client.set(pair, rate)
            print(f"[OK] set rate {pair} = {rate}")

        print("✅ Test rates successfully populated in Redis")

    finally:
        await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
