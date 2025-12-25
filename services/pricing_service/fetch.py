# services/pricing_service/fetch.py
import asyncio
from providers.binance import get_rates as get_binance_rates
from providers.fallback import get_rates as get_fallback_rates
from providers.fx import get_rates as get_fx_rates
from redis_repo.rates import save_rate, RATE_TTL_SECONDS
from utils.time import utc_now_iso
from . import settings


async def fetch_and_save_rates():
    """
    Fetch rates from multiple providers (crypto + fiat) and save to Redis.
    Priority:
      1. Binance (crypto)
      2. FX (fiat)
      3. Fallback if provider fails
    """
    all_rates = []

    # --- Binance (crypto) ---
    try:
        crypto_rates = await get_binance_rates(settings.CRYPTO_SYMBOLS)
        if crypto_rates:
            all_rates.extend(crypto_rates)
    except Exception as e:
        print(f"[Pricing][Binance] Ошибка: {e}")

    # --- FX (fiat) ---
    try:
        fx_rates = await get_fx_rates(settings.FIAT_BASE, settings.FIAT_QUOTES)
        if fx_rates:
            all_rates.extend(fx_rates)
    except Exception as e:
        print(f"[Pricing][FX] Ошибка: {e}")

    # --- Fallback (на случай, если что-то не пришло) ---
    if not all_rates:
        print("[Pricing] Все провайдеры недоступны, используем fallback")
        fallback_rates = await get_fallback_rates(settings.FIAT_BASE, settings.FIAT_QUOTES + ["BTC"])
        all_rates.extend(fallback_rates)

    # --- Сохраняем все курсы в Redis ---
    for rate in all_rates:
        await save_rate(
            rate.base,
            rate.quote,
            float(rate.rate),
            settings.RATE_TTL_SECONDS,
            rate.source,
            rate.updated_at or utc_now_iso(),
        )

    return all_rates


# --- Фоновый цикл обновления ---
async def start_periodic_fetch(interval: int = 60):
    while True:
        try:
            await fetch_and_save_rates()
        except Exception as e:
            print(f"[Pricing] Ошибка при fetch rates: {e}")
        await asyncio.sleep(interval)


# ПЕРЕПИСАТЬ!!!
