# pricing_service/utils/normalizer.py

STABLES = {"USDT"}

def normalize_symbol(symbol: str):
    for stable in STABLES:
        if symbol.endswith(stable):
            base = symbol[:-len(stable)]
            quote = stable
            return base, quote
    return None
