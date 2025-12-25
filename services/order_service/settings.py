import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://exchange:exchange@localhost:5432/exchange")

ORDER_TTL_SECONDS = int(os.getenv("ORDER_TTL_SECONDS", "60"))
IDEMPOTENCY_TTL_SECONDS = int(os.getenv("IDEMPOTENCY_TTL_SECONDS", "3600"))
