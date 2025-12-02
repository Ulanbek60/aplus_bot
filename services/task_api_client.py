import aiohttp
from config import TASK_API_URL
import asyncio


class TaskAPIClient:
    def __init__(self):
        self.token = None

    async def get_token(self):
        """Получаем токен с /getToken"""
        url = f"{TASK_API_URL}/getToken"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception(f"Task API error {resp.status}")

                data = await resp.json()

                if "token" not in data:
                    raise Exception("Task API returned invalid token")

                self.token = data["token"]
                return self.token

    async def request(self, method: str, endpoint: str, params=None, data=None):
        """Делаем запрос с токеном X-CSRF-TOKEN"""
        if self.token is None:
            await self.get_token()

        url = f"{TASK_API_URL}{endpoint}"

        headers = {
            "X-CSRF-TOKEN": self.token,
            "Accept": "*/*"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=data
            ) as resp:

                if resp.status == 419:
                    # Токен умер → получаем новый и повторяем
                    await self.get_token()
                    return await self.request(method, endpoint, params, data)

                result = await resp.json()
                return result


# создаём глобальный экземпляр клиента
task_api = TaskAPIClient()
