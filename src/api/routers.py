from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import StreamingResponse

from src.api.deps import get_inference_server
from src.logger_config import logger
from src.model.triton_infer import InferenceServer
from src.utils.masking import create_mask, mask_prompt
from src.utils.streaming import proxy_stream_llm

router = APIRouter()


@router.post("/chat/completions")
async def chat(
    request: Request,
    authorization: str = Header(),
    inference_server: InferenceServer = Depends(get_inference_server),
):
    body = await request.json()
    access_token = authorization.split()[-1]  # Bearer <token>
    model, message = body["model"], body["messages"][-1].get("content", "")
    triton_response = await inference_server.infer_text(message)
    predictions, tokens = triton_response["predictions"], triton_response["tokens"]
    mask_mapping = create_mask(predictions, tokens)
    logger.info(f"MASK MAPPING> {mask_mapping}")
    masked_prompt, unmask_mapping = mask_prompt(message, mask_mapping)

    logger.info(f"MASKED PROMPT: {masked_prompt}")

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
