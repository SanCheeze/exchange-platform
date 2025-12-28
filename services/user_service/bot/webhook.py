from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

from bot.bot import bot, dp
from settings import WEBHOOK_PATH


def setup_webhook(app: web.Application):
    handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )

    handler.register(app, path=WEBHOOK_PATH)
