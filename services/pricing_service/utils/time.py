# services/pricing_service/utils/time.py

from datetime import datetime, timezone


def utc_now_iso() -> str:
    """
    Возвращает текущую временную метку UTC в ISO формате
    (например: "2025-02-14T15:30:22.123456+00:00").
    """
    return datetime.now(timezone.utc).isoformat()
