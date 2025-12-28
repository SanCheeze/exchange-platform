# user_service/app.py


from aiohttp import web

from settings import DATABASE_URI
from database.pg import init_pg
from logic.users import add_user, get_user, edit_user


async def init_app():
    app = web.Application()

    # DB
    app.on_startup.append(lambda app: init_pg(DATABASE_URI))

    # Routes
    app.router.add_post("/users", add_user)
    app.router.add_get("/users/{telegram_id}", get_user)
    app.router.add_patch("/users/{telegram_id}", edit_user)

    return app


if __name__ == "__main__":
    web.run_app(init_app(), port=8083)
