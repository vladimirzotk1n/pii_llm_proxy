from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from src.api.deps import get_inference_server
from src.model.triton_infer import InferenceServer
from src.utils.masking import create_mask, mask_prompt
from src.utils.streaming import proxy_stream_llm

router = APIRouter()


@router.post("/chat/completions")
async def chat(
    request: Request,
    inference_server: InferenceServer = Depends(get_inference_server),
):
    allowed_headers = {
        "authorization": request.headers.get("authorization"),
        "content-type": "application/json",
    }
    body = await request.json()
    message = body["messages"][-1]["content"]
    triton_response = await inference_server.infer_text(message)
    predictions, tokens = triton_response["predictions"], triton_response["tokens"]
    mask_mapping = create_mask(predictions, tokens)
    masked_prompt, unmask_mapping = mask_prompt(message, mask_mapping)

    body["messages"][-1]["content"] = masked_prompt

    async def event_stream():
        async for chunk in proxy_stream_llm(body, allowed_headers, unmask_mapping):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}
