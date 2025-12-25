import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 5))

# какие пары мы хотим поддерживать
FIAT_BASE = "USD"
FIAT_SYMBOLS = ["RUB", "THB"]

CRYPTO_SYMBOLS = ["RUBUSDT", "THBUSDT"]
