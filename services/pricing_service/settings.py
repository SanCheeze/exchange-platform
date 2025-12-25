import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 30))  # seconds

# --- Список валют и символов ---
CRYPTO_SYMBOLS = ["BTCUSDT", "ETHUSDT", "USDTUSD"]  # криптовалютные пары
FIAT_BASE = "USD"                                    # базовая валюта для фиата
FIAT_QUOTES = ["EUR", "GBP", "JPY"]                  # фиатные валюты для конвертации

