# services/order_service/app.py

from aiohttp import web

from kafka_worker import process_outbox
from logic.orders import (
    init_redis,
    init_database,
    close_redis,
    healthcheck,
    create_order,
    confirm_order,
)


# =====================
# APP FACTORY
# =====================
async def create_app():
    app = web.Application()

    app.router.add_get("/health", healthcheck)
    app.router.add_post("/orders", create_order)
    app.router.add_post("/orders/{order_id}/confirm", confirm_order)

    app.on_startup.append(init_redis)
    app.on_startup.append(init_database)
    app.on_startup.append(process_outbox)

    app.on_cleanup.append(close_redis)

    return app


# =====================
# ENTRYPOINT
# =====================
def main():
    web.run_app(
        create_app(),
        host="0.0.0.0",
        port=8082,
    )


if __name__ == "__main__":
    main()
