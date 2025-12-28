# user_service/logic/users.py

import uuid
from aiohttp import web

from database.users import (
    insert_user,
    get_user_by_telegram_id,
    update_user,
)
from utils.time import utc_now_iso


# =====================
# ADD USER
# =====================
async def add_user(
    telegram_id: int,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
):
    existing = await get_user_by_telegram_id(telegram_id)
    if existing:
        return dict(existing)

    ts = utc_now_iso()

    user = {
        "id": uuid.uuid4(),
        "telegram_id": telegram_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "commission": 0.0100,
        "total_volume": 0,
        "payment_info": None,
        "created_at": ts,
        "updated_at": ts,
    }

    await insert_user(user)
    return user


# =====================
# GET USER
# =====================
async def get_user(request: web.Request):
    telegram_id = int(request.match_info["telegram_id"])

    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        return web.json_response(
            {"error": "USER_NOT_FOUND"},
            status=404,
        )

    return web.json_response(dict(user), status=200)


# =====================
# EDIT USER
# =====================
async def edit_user(request: web.Request):
    telegram_id = int(request.match_info["telegram_id"])
    data = await request.json()

    await update_user(telegram_id, data)

    user = await get_user_by_telegram_id(telegram_id)
    return web.json_response(dict(user), status=200)
