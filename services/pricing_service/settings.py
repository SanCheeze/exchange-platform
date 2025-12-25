# pricing_service/settings.py

import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

FETCH_INTERVAL_SECONDS = int(os.getenv("UPDATE_INTERVAL", 10))  # seconds

# FX
FIAT_BASE = "USD"
FIAT_QUOTES = ["EUR", "GBP", "THB"]

# Binance
CRYPTO_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "USDTTHB",
]

REDIS_RATE_TTL = 120
