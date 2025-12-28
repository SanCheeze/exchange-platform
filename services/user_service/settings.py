# user_service/settings.py

import os


SERVICE_NAME = "user_service"

BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "8186129902:AAHSCuyrPbzdtPSDZVxLqgzINr5DVvH2XWQ")
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "https://sweetmeal-tameka-sheddable.ngrok-free.dev")  # https://your-domain.com
WEBHOOK_PATH = "/tg/webhook"
WEBHOOK_URL = f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}"

WEBAPP_URL = os.getenv("WEBAPP_URL", "https://sweetmeal-tameka-sheddable.ngrok-free.dev")  # https://your-webapp.com

DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql://exchange:exchange@localhost:5432/exchange",
)