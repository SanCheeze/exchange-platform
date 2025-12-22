from datetime import datetime
from .pg import get_pool

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
