import json

import httpx

from src.config import get_settings
from src.utils.masking import Unmasker

settings = get_settings()

SYSTEM_PROMPT = (
    "You are a helpful assistant.\n\n"
    "User input may contain redacted sensitive fields represented as placeholders "
    "like [[TYPE_i]]. Treat these placeholders as normal parts of the text.\n"
    "Do not comment on them, do not explain them, and do not treat them as special.\n"
    "Use them exactly as they appear in the input.\n\n"
    "Never modify, infer, replace, or expand placeholders.\n"
    "Do not attempt to guess their meaning or contents.\n\n"
    "Do not repeat the user input. Respond directly to the question.\n\n"
    "Input:\n"
)


async def stream_llm(body: dict, headers: dict):
    body["messages"] = [{"role": "system", "content": SYSTEM_PROMPT}] + body["messages"]
    async with httpx.AsyncClient(
        timeout=None, verify=False
    ) as client:  # TODO: сделать с TLS
        async with client.stream(
            "POST",
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            json=body,
            headers=headers,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                if line.startswith("data:"):
                    data = line.removeprefix("data:").strip()
                    if data == "[DONE]":
                        break
                    yield data


async def proxy_stream_llm(body: dict, headers: dict, mapping: dict[str, str]):
    unmasker = Unmasker(mapping)

    async for raw_chunk in stream_llm(body, headers):
        if raw_chunk == "[DONE]":
            break

        try:
            data = json.loads(raw_chunk)
        except BaseException:
            continue

        delta = data["choices"][0].get("delta", {})
        content = delta.get("content", "")

        if not content:
            continue

        processed_chunk = unmasker.process(content)

        if processed_chunk:
            yield processed_chunk
