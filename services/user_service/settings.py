import os


SERVICE_NAME = "user_service"

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL")  # https://your-domain.com
WEBHOOK_PATH = "/tg/webhook"
WEBHOOK_URL = f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}"

WEBAPP_URL = os.getenv("WEBAPP_URL")  # https://your-webapp.com

DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql://exchange:exchange@localhost:5432/exchange",
)