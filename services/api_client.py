# services/api_client.py
import aiohttp
from config import BACKEND_URL
import logging

logger = logging.getLogger(__name__)


class BackendAPI:
    def __init__(self):
        self.base_url = BACKEND_URL.rstrip("/")

    async def get(self, path: str):
        url = f"{self.base_url}{path}"

        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    text = await resp.text()

                    try:
                        return resp.status, await resp.json()
                    except:
                        logger.error(f"Invalid JSON from backend: {text}")
                        return resp.status, text
        except Exception as e:
            logger.error(f"GET failed: {e}")
            return 500, None

    async def post(self, path: str, payload: dict):
        url = f"{self.base_url}{path}"

        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as resp:
                    text = await resp.text()

                    try:
                        return resp.status, await resp.json()
                    except:
                        logger.error(f"Invalid JSON from backend: {text}")
                        return resp.status, text
        except Exception as e:
            logger.error(f"POST failed: {e}")
            return 500, None


# создаём глобальный клиент
backend_api = BackendAPI()
