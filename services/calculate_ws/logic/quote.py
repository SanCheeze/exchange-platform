import time


COMMISSION = 0.005


def calc_quote(amount: float, rate: float) -> float:
    return round(amount * rate * (1 - COMMISSION), 2)


def build_quote(
    *,
    quote_id: str,
    session_id: str,
    from_currency: str,
    to_currency: str,
    amount_in: float,
    rate: float,
    amount_out: float
) -> dict:
    return {
        "quote_id": quote_id,
        "session_id": session_id,
        "from": from_currency,
        "to": to_currency,
        "amount_in": amount_in,
        "amount_out": amount_out,
        "rate": rate,
        "commission": COMMISSION,
        "created_at": int(time.time())
    }
