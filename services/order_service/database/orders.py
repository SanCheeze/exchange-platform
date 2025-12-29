# order_service/database/orders.py

from datetime import datetime

from database.pg import get_pool
from database.events import send_to_outbox
from domain.order_status import OrderStatus


async def insert_order(order: dict):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():

            await conn.execute(
                """
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
                """,
                order["id"],
                order["order_id"],
                order["status"],
                order["quote_id"],
                order["pair"],
                order["amount_in"],
                order["amount_out"],
                order["rate"],
                order["commission"],
                order["client_id"],
                order["session_id"],
                order["created_at"],
                order["updated_at"],
            )

            await send_to_outbox(
                conn=conn,
                aggregate_type="order",
                aggregate_id=order["order_id"],
                event_type="order.inserted",
                event_payload=order,
            )


async def get_order(order_id: str):
    pool = get_pool()

    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM orders WHERE order_id = $1",
            order_id,
        )


async def update_order_status(order_id: str, status: str, updated_at: datetime):
    pool = get_pool()

    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE orders
            SET status = $1,
                updated_at = $2
            WHERE order_id = $3
            """,
            status,
            updated_at,
            order_id,
        )


async def confirm_order(order_id: str, event_payload: dict) -> bool:
    pool = get_pool()
    ts = datetime.utcnow()

    async with pool.acquire() as conn:
        async with conn.transaction():

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

            if result == "UPDATE 0":
                return False

            await send_to_outbox(
                conn=conn,
                aggregate_type="order",
                aggregate_id=order_id,
                event_type="order.confirmed",
                event_payload=event_payload,
            )

    return True
