import asyncio
import os
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

RATES = {
    "USD_EUR": 0.95,
    "EUR_USD": 1.05,
    "USD_USDT": 1.0,
    "USDT_USD": 1.0,
    "EUR_USDT": 1.02,
    "USDT_EUR": 0.98
}

async def main():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    for k, v in RATES.items():
        await r.set(k, v)
    await r.aclose()
    print("Test rates populated in Redis")

if __name__ == "__main__":
    asyncio.run(main())
