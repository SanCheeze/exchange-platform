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
async def add_user(request: web.Request):
    data = await request.json()

    telegram_id = data.get("telegram_id")
    if not telegram_id:
        return web.json_response(
            {"error": "TELEGRAM_ID_REQUIRED"},
            status=400,
        )

    existing = await get_user_by_telegram_id(telegram_id)
    if existing:
        return web.json_response(dict(existing), status=200)

    ts = utc_now_iso()

    user = {
        "id": uuid.uuid4(),
        "telegram_id": telegram_id,
        "username": data.get("username"),
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "commission": 0.0100,
        "total_volume": 0,
        "payment_info": None,
        "created_at": ts,
        "updated_at": ts,
    }

    await insert_user(user)

    return web.json_response(user, status=201)


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
