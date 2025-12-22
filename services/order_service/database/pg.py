import asyncpg
from pathlib import Path

_pool: asyncpg.Pool | None = None


async def init_pg(dsn: str):
    global _pool
    _pool = await asyncpg.create_pool(dsn)

    schema_path = Path(__file__).parent / "schema.sql"
    schema = schema_path.read_text()

    async with _pool.acquire() as conn:
        await conn.execute(schema)


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("PostgreSQL not initialized")
    return _pool
