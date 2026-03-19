from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routers import router

# from src.redis.redis_db import RedisDB
# TODO: add redis back
from src.config import get_settings
from src.logger_config import logger
from src.model.triton_infer import InferenceServer
from src.utils.gigachat_token import TokenManager

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI backend")
    # redis = RedisDB()
    # app.state.redis = redis

    app.state.inference_server = InferenceServer()
    app.state.token_manager = TokenManager(settings.auth_token, settings.scope)
    yield
    logger.info("Finishing FastAPI backend")
    # await redis.close()
    await app.state.inference_server.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router=router)
