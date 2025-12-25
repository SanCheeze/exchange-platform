from decimal import Decimal

from redis_repo.rates import get_rate
from redis_repo.quotes import save_quote

from logic.quote import build_quote
from utils.ids import generate_quote_id


class QuoteEngine:
    def __init__(self, redis):
        self.redis = redis

    async def compute(self, session_id: str, from_cur: str, to_cur: str, amount: float):
        amount_dec = Decimal(str(amount))

        # 1) прямой курс
        r = await get_rate(self.redis, from_cur, to_cur)
        if r is not None:
            rate_dec = Decimal(str(r))
            amount_out = (amount_dec * rate_dec).quantize(Decimal("0.0001"))
        else:
            # 2) обратный курс
            r_inv = await get_rate(self.redis, to_cur, from_cur)
            if r_inv is None:
                raise ValueError(f"No rate for {from_cur}->{to_cur}")

            rate_dec = Decimal(str(r_inv))
            amount_out = (amount_dec / rate_dec).quantize(Decimal("0.0001"))

        quote_id = generate_quote_id()
        quote = build_quote(
            quote_id=quote_id,
            session_id=session_id,
            from_currency=from_cur,
            to_currency=to_cur,
            amount_in=str(amount_dec),
            rate=str(rate_dec),
            amount_out=str(amount_out),
        )

        
        from redis_repo.quotes import save_quote
        await save_quote(self.redis, quote_id, quote)

        return {
            "quote_id": quote_id,
            "amount_out": str(amount_out),
            # "expires_in": quote["expires_at"] - quote["created_at"],
        }
