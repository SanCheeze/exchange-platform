# user_service/database/users.py

from database.pg import get_pool
from database.events import send_to_outbox


async def insert_user(user: dict):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():

            await conn.execute(
                """
                INSERT INTO users (
                    id,
                    telegram_id,
                    username,
                    first_name,
                    last_name,
                    commission,
                    total_volume,
                    payment_info,
                    created_at,
                    updated_at
                )
                VALUES (
                    $1,$2,$3,$4,$5,$6,$7,$8,$9,$10
                )
                """,
                user["id"],
                user["telegram_id"],
                user["username"],
                user["first_name"],
                user["last_name"],
                user["commission"],
                user["total_volume"],
                user["payment_info"],
                user["created_at"],
                user["updated_at"],
            )

            await send_to_outbox(
                conn=conn,
                aggregate_type="user",
                aggregate_id=str(user["id"]),  # ✅ internal id
                event_type="user.created",
                event_payload=user,
            )


async def get_user_by_telegram_id(telegram_id: int):
    pool = get_pool()

    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE telegram_id = $1",
            telegram_id,
        )


async def update_user(telegram_id: int, fields: dict):
    if not fields:
        return False

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():

            user = await conn.fetchrow(
                "SELECT id FROM users WHERE telegram_id = $1",
                telegram_id,
            )

            if not user:
                return False

            sets = []
            values = []
            idx = 1

            for k, v in fields.items():
                sets.append(f"{k} = ${idx}")
                values.append(v)
                idx += 1

            query = f"""
                UPDATE users
                SET {", ".join(sets)}, updated_at = NOW()
                WHERE telegram_id = ${idx}
            """

            await conn.execute(query, *values, telegram_id)

            await send_to_outbox(
                conn=conn,
                aggregate_type="user",
                aggregate_id=str(user["id"]),
                event_type="user.updated",
                event_payload={
                    "telegram_id": telegram_id,
                    "updated_fields": fields,
                },
            )

    return True
