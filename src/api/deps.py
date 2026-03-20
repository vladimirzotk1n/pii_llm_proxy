from fastapi import Request


async def get_redis(request: Request):
    return request.app.state.redis


async def get_inference_server(request: Request):
    return request.app.state.inference_server
