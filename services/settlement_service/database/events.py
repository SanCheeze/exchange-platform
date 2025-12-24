# settlement_service/database/events.py

async def is_event_processed(conn, event_id: str) -> bool:
    row = await conn.fetchrow(
        "SELECT 1 FROM processed_events WHERE event_id = $1",
        event_id,
    )
    return row is not None


async def mark_event_processed(
    conn,
    event_id: str,
    topic: str,
    partition: int,
    offset: int,
):
    await conn.execute(
        """
        INSERT INTO processed_events (event_id, topic, kafka_partition, kafka_offset)
        VALUES ($1, $2, $3, $4)
        """,
        event_id,
        topic,
        partition,
        offset,
    )
