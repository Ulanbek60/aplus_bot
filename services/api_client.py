import aiohttp
from config import BACKEND_URL


class APIClient:
    def __init__(self):
        self.base_url = BACKEND_URL.rstrip("/")

    async def get(self, path):
        url = f"{self.base_url}{path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                return resp.status, data

    async def post(self, path, json):
        url = f"{self.base_url}{path}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json) as resp:
                data = await resp.json()
                return resp.status, data


api_client = APIClient()
