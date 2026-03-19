import json

import httpx

from src.config import get_settings
from src.logger_config import logger
from src.utils.masking import Unmasker

settings = get_settings()


async def stream_llm(model: str, prompt: str, access_token: str):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],  # TODO: добавить память
        "stream": True,
    }

    async with httpx.AsyncClient(
        timeout=None, verify=False
    ) as client:  # TODO: сделать с TLS
        async with client.stream(
            "POST",
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            json=payload,
            headers=headers,
        ) as response:
            logger.info(f"{response}")
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    yield data


async def proxy_stream_llm(
    model: str, masked_prompt: str, mapping: dict[str, str], access_token: str
):
    unmasker = Unmasker(mapping)

    async for raw_chunk in stream_llm(model, masked_prompt, access_token):
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
