# settlement_service/handlers/handler.py
import os
import json
import asyncio
import uuid
from decimal import Decimal

from database.events import is_event_processed, mark_event_processed


async def handle_event(conn, msg):
    """
    Обработка одного Kafka-сообщения.
    ВАЖНО: работает внутри транзакции БД.
    """
    event_id = f"{msg.topic}:{msg.partition}:{msg.offset}"
    payload = json.loads(msg.value)

    # 1️⃣ идемпотентность
    if await is_event_processed(conn, event_id):
        return

    # 2️⃣ бизнес-логика
    await conn.execute(
        """
        INSERT INTO settlements (
            id,
            order_id,
            pair,
            amount_in,
            amount_out,
            rate
        )
        VALUES ($1, $2, $3, $4, $5, $6)
        """,
        uuid.uuid4(),
        payload["order_id"],
        payload["pair"],
        Decimal(payload["amount_in"]),
        Decimal(payload["amount_out"]),
        Decimal(payload["rate"]),
    )

    # 3️⃣ фиксируем обработку события
    await mark_event_processed(
        conn,
        event_id,
        msg.topic,
        msg.partition,
        msg.offset,
    )