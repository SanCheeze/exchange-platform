# settlement_service/settings.py

import os

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = "order.confirmed"
GROUP_ID = "settlement-service"

DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql://exchange:exchange@localhost:5432/exchange",
)
