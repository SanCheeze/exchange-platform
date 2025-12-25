from redis.asyncio import Redis

from utils.ids import generate_quote_id
from redis_repo.rates import get_rate
from redis_repo.quotes import save_quote, QUOTE_TTL_SECONDS
from logic.quote import calc_quote, build_quote


class QuoteEngine:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_quote(
        self,
        *,
        session_id: str,
        from_currency: str,
        to_currency: str,
        amount: float,
    ) -> dict:
        rate = await get_rate(self.redis, from_currency, to_currency)
        if rate is None:
            raise ValueError(f"No rate for {from_currency}->{to_currency}")

        amount_out = calc_quote(amount, rate)
        quote_id = generate_quote_id()

        quote = build_quote(
            quote_id=quote_id,
            session_id=session_id,
            from_currency=from_currency,
            to_currency=to_currency,
            amount_in=amount,
            rate=rate,
            amount_out=amount_out,
        )

        await save_quote(self.redis, quote_id, quote)

        return {
            "quote_id": quote_id,
            "amount_out": amount_out,
            "expires_in": QUOTE_TTL_SECONDS,
        }
