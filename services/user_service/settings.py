import os

DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql://exchange:exchange@localhost:5432/exchange",
)

SERVICE_NAME = "user_service"
