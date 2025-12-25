import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 30))  # seconds

BASE_CURRENCIES = ["USD", "TBH", "RUB"]
TARGET_CURRENCIES = ["USD", "TBH", "RUB"]
