import asyncio
import getpass
import uuid

import httpx


class TokenManager:
    AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    def __init__(self, auth_key: str, scope: str = "GIGACHAT_API_PERS"):
        self.client = httpx.AsyncClient(timeout=30, verify=False)
        self.auth_key = auth_key
        self.scope = scope

    async def get_token(self) -> str:
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
        return data["access_token"]


if __name__ == "__main__":
    auth_key = getpass.getpass("Enter your Authorization key: ")
    print("\n\n")
    token_manager = TokenManager(auth_key)

    access_token = asyncio.run(token_manager.get_token())
    print(f"Your access token: \n\n{access_token}")
