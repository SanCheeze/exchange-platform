import uuid


def generate_session_id() -> str:
    return str(uuid.uuid4())


def generate_quote_id() -> str:
    return "q_" + uuid.uuid4().hex[:12]
