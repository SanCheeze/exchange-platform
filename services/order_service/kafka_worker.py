# kafka_worker.py
import asyncio
import json
from datetime import datetime
from database.pg import get_pool
from aiokafka import AIOKafkaProducer


KAFKA_BOOTSTRAP = "localhost:9092"
POLL_INTERVAL = 1.0  # секунды
BATCH_SIZE = 50


async def process_outbox(app):
    """
    Фоновая задача для чтения outbox_events и отправки их в Kafka.
    При старте приложения aiohttp передаст сюда `app`.
    """
    pool = get_pool()
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP)
    await producer.start()

    async def worker():
        try:
            while True:
                async with pool.acquire() as conn:
                    rows = await conn.fetch(
                        "SELECT * FROM outbox_events WHERE processed_at IS NULL ORDER BY created_at LIMIT $1",
                        BATCH_SIZE,
                    )

                    for row in rows:
                        payload = json.loads(row["payload"])
                        topic = row["event_type"]

                        try:
                            await producer.send_and_wait(
                                topic, json.dumps(payload).encode("utf-8")
                            )
                            # Отмечаем событие как обработанное
                            await conn.execute(
                                "UPDATE outbox_events SET processed_at = $1 WHERE id = $2",
                                datetime.utcnow(),
                                row["id"],
                            )
                        except Exception as e:
                            print(f"Failed to publish {row['id']} to Kafka: {e}")
                            # оставляем событие для retry

                await asyncio.sleep(POLL_INTERVAL)
        finally:
            await producer.stop()

    # запускаем воркер как фоновую задачу
    app['outbox_task'] = asyncio.create_task(worker())
