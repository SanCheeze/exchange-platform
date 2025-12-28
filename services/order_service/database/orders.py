# order_service/database/orders.py

import uuid
import json
from datetime import datetime

from database.pg import get_pool
from database.events import send_to_outbox
from domain.order_status import OrderStatus


async def insert_order(order: dict):
    """
    Сохраняет заказ в БД.
    Ожидается, что:
    - order['id'] — UUID объект
    - order['created_at'], order['updated_at'] — datetime объекты
    """
    pool = get_pool()  # возвращает asyncpg pool

    query = """
        INSERT INTO orders (
            id,
            order_id,
            status,
            quote_id,
            pair,
            amount_in,
            amount_out,
            rate,
            commission,
            client_id,
            session_id,
            created_at,
            updated_at
        ) VALUES (
            $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13
        )
    """

    async with pool.acquire() as conn:
        await pool.execute(
            query,
            order["id"],           # UUID
            order["order_id"],     # str
            order["status"],       # str
            order["quote_id"],     # str
            order["pair"],         # str
            order["amount_in"],    # float
            order["amount_out"],   # float
            order["rate"],         # float
            order["commission"],   # float
            order["client_id"],    # str | None
            order["session_id"],   # str
            order["created_at"],   # datetime
            order["updated_at"],   # datetime
        )

        await send_to_outbox(
            conn=conn,
            aggregate_type="order",
            aggregate_id=order_id,
            event_type="order.inserted",
            event_payload=order
        )


async def get_order(order_id: str):
    pool = get_pool()

    query = """
        SELECT *
        FROM orders
        WHERE order_id = $1
    """

    async with pool.acquire() as conn:
        return await conn.fetchrow(query, order_id)


async def update_order_status(order_id: str, status: str, updated_at: datetime):
    pool = get_pool()

    query = """
        UPDATE orders
        SET status = $1,
            updated_at = $2
        WHERE order_id = $3
    """
    await conn.execute(
        query,
        status,
        updated_at,
        order_id,
    )


async def confirm_order(order_id: str, event_payload: dict):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():

            # 1️⃣ Обновляем заказ
            result = await conn.execute(
                """
                UPDATE orders
                SET status = $1,
                    updated_at = $2
                WHERE order_id = $3
                  AND status = $4
                """,
                OrderStatus.CONFIRMED,
                ts,
                order_id,
                OrderStatus.CREATED,
            )

            # если не обновили — значит уже confirmed или invalid state
            if result == "UPDATE 0":
                return False

            await send_to_outbox(
                conn=conn,
                aggregate_type="order",
                aggregate_id=order_id,
                event_type="order.confirmed",
                event_payload=event_payload
            )
