# settlement_service/app.py

import asyncio
from aiokafka import AIOKafkaConsumer
from database.pg import init_pg, get_pool

from settings import KAFKA_BOOTSTRAP, TOPIC, GROUP_ID, DATABASE_URI


async def main():
    await init_pg(DATABASE_URI)
    pool = get_pool()

    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID,
        enable_auto_commit=False,
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
