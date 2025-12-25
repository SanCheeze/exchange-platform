# services/pricing_service/settings.py

import os
from dotenv import load_dotenv
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Redis TTL for each rate (seconds)
REDIS_RATE_TTL = int(os.getenv("REDIS_RATE_TTL", 120))

# Binance WebSocket stream
BINANCE_WS_URL = os.getenv(
    "BINANCE_WS_URL",
    "wss://stream.binance.com:9443/ws/!ticker@arr"
)

# stablecoin used as quote for pricing
STABLE_QUOTE = os.getenv("STABLE_QUOTE", "USDT")
