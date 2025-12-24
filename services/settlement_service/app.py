# settlement_service/app.py
import os
import json
import asyncio
import uuid
from decimal import Decimal
from datetime import datetime

from aiokafka import AIOKafkaConsumer
from database.pg import init_pg, get_pool
from database.events import is_event_processed, mark_event_processed


KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = "order.confirmed"
GROUP_ID = "settlement-service"

DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql://exchange:exchange@localhost:5432/exchange",
)


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


async def main():
    await init_pg(DATABASE_URI)
    pool = get_pool()

    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID,
        enable_auto_commit=False,      # ❗ обязательно
        auto_offset_reset="earliest",
    )

    await consumer.start()
    print("Settlement Service Started\n")

    try:
        async for msg in consumer:
            try:
                async with pool.acquire() as conn:
                    async with conn.transaction():
                        await handle_event(conn, msg)

                # ✅ commit offset ТОЛЬКО после commit БД
                await consumer.commit()

                print(
                    f"[OK]\t{msg.topic} "
                    f"p={msg.partition} "
                    f"o={msg.offset}"
                )

            except Exception as e:
                # ❌ offset НЕ коммитим → Kafka пришлёт событие снова
                print(
                    "[ERROR]\t"
                    f"{msg.topic} "
                    f"p={msg.partition} "
                    f"o={msg.offset} → {e}"
                )

    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
