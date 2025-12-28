# user_service/bot/handlers.py

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo

from settings import WEBAPP_URL
from database.users import get_user_by_telegram_id, insert_user
from utils.time import utc_now
import uuid


router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message):
    tg_user = message.from_user

    existing = await get_user_by_telegram_id(tg_user.id)
    if not existing:
        ts = utc_now()
        await insert_user(
            {
                "id": uuid.uuid4(),
                "telegram_id": tg_user.id,
                "username": tg_user.username,
                "first_name": tg_user.first_name,
                "last_name": tg_user.last_name,
                "commission": 0.0100,
                "total_volume": 0,
                "payment_info": None,
                "created_at": ts,
                "updated_at": ts,
            }
        )

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🚀 Open Web App",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ]
        ]
    )

    await message.answer(
        "Добро пожаловать 👋\n\nОткройте Web App для работы с сервисом.",
        reply_markup=keyboard,
    )
