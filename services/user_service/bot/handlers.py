# user_service/bot/handlers.py

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo

from logic.users import add_user

router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message):
    user = message.from_user

    await add_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🚀 Open Web App",
                    web_app=WebAppInfo(url="https://your-webapp.com"),
                )
            ]
        ]
    )

    await message.answer(
        "Добро пожаловать 👋\n\nОткройте Web App для работы с сервисом.",
        reply_markup=keyboard,
    )
