import time
import uuid
from dataclasses import dataclass

import httpx


@dataclass
class TokenCache:
    access_token: str
    expires_at: float

    def is_valid(self, buffer: int = 30):
        return time.time() < (self.expires_at - buffer)


class TokenManager:
    AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    def __init__(self, auth_key: str, scope: str = "GIGACHAT_API_PERS"):
        self.token_cache: TokenCache | None = None
        self.client = httpx.AsyncClient(timeout=30, verify=False)
        self.auth_key = auth_key
        self.scope = scope

    async def get_token(self):
        if self.token_cache and self.token_cache.is_valid():
            return self.token_cache.access_token

        await self._refresh_token()
        return self.token_cache.access_token

    async def _refresh_token(self) -> str:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {self.auth_key}",
        }
        response = await self.client.post(
            self.AUTH_URL, headers=headers, data={"scope": self.scope}
        )

        response.raise_for_status()
        data = response.json()

        self.token_cache = TokenCache(
            access_token=data["access_token"], expires_at=data["expires_at"] / 1000
        )


if __name__ == "__main__":
    ak = "<token>"
    tm = TokenManager(ak)
    import asyncio

    print(asyncio.run(tm.get_token()))
