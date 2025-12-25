# services/pricing_service/utils/normalizer.py

from settings import STABLE_QUOTE

def normalize_symbol(symbol: str):
    """
    Если символ заканчивается на STABLE_QUOTE (например BTCUSDT),
    возвращает tuple (base, quote). Иначе None.
    """
    if symbol.endswith(STABLE_QUOTE):
        base = symbol[:-len(STABLE_QUOTE)]
        quote = STABLE_QUOTE
        return base, quote
    return None
