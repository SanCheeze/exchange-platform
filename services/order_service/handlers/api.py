from aiohttp import web
from logic.orders import create_order_logic
from domain.order_status import OrderStatus
from redis_repo.orders import get_cached_order


async def create_order(request: web.Request):
    try:
        data = await request.json()
        order = await create_order_logic(request.app["redis"], data)
        return web.json_response(order, status=201)
    except ValueError as e:
        return web.json_response({"error": str(e)}, status=400)


async def get_order(request: web.Request):
    order_id = request.match_info["order_id"]
    order = await get_cached_order(request.app["redis"], order_id)
    if order:
        return web.json_response(order)
    return web.json_response({"error": "ORDER_NOT_FOUND"}, status=404)
