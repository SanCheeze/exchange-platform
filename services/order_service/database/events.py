# order_service/database/events.py

import uuid
import json
from datetime import datetime

from .pg import get_pool


async def send_to_outbox(
        conn,
        aggregate_type: str,
        aggregate_id: int,
        event_type: str,
        event_payload: dict
    ):
    await conn.execute(
                """
                INSERT INTO outbox_events (
                    id,
                    aggregate_type,
                    aggregate_id,
                    event_type,
                    payload,    
                    created_at
                ) VALUES ($1,$2,$3,$4,$5,$6)
                """,
                uuid.uuid4(),
                aggregate_type,
                aggregate_id,
                event_type,
                json.dumps(event_payload),
                datetime.utcnow(),
            )
    return True
