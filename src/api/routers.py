import requests
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# from redis.redis_db import RedisDB
from src.api.deps import get_inference_server, get_redis, get_token
from src.model.triton_infer import InferenceServer
from src.utils.masking import create_mask, mask_prompt
from src.utils.streaming import proxy_stream_llm

router = APIRouter()


@router.post("/chat/completions")
async def chat(
    request: Request,
    # redis: RedisDB = Depends(get_redis),
    inference_server: InferenceServer = Depends(get_inference_server),
    access_token: str = Depends(get_token),
):
    body = await request.json()
    model, message = body["model"], body["messages"][-1].get("content", "")
    triton_response = await inference_server.infer_text(message)
    predictions, tokens = triton_response["predictions"], triton_response["tokens"]
    mask_mapping = create_mask(predictions, tokens)
    masked_prompt, unmask_mapping = mask_prompt(message, mask_mapping)

    async def event_stream():
        async for chunk in proxy_stream_llm(
            model, masked_prompt, unmask_mapping, access_token
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}
