from models import ProviderResult


def use_last_known(rates: list) -> ProviderResult:
    return ProviderResult(
        ok=False,
        rates=rates,
        error="using last known rates",
    )
