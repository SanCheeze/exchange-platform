from decimal import Decimal
from redis_repo.rates import get_rate


async def convert(redis, amount: Decimal, from_cur: str, to_cur: str) -> Decimal:
    """
    Пытаемся:
    1) from → to
    2) to → from (деление)
    """

    direct = await get_rate(redis, from_cur, to_cur)
    if direct:
        return amount * direct

    reverse = await get_rate(redis, to_cur, from_cur)
    if reverse:
        return amount / reverse

    raise ValueError(f"No conversion path {from_cur}->{to_cur}")
