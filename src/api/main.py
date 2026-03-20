from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routers import router

# TODO: add redis back
from src.config import get_settings
from src.logger_config import logger
from src.model.triton_infer import InferenceServer

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI backend")

    app.state.inference_server = InferenceServer()
    yield
    logger.info("Finishing FastAPI backend")
    await app.state.inference_server.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router=router)
