from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from settings import BOT_TOKEN


bot = Bot(
    token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)

dp = Dispatcher()
