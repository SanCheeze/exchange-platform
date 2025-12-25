from datetime import datetime, timezone


def utc_now_iso() -> str:
    """Возвращает текущий UTC в ISO формате"""
    return datetime.now(timezone.utc).isoformat()
