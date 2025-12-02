# services/api_client.py
import aiohttp
import asyncio
from config import BACKEND_URL
import logging

logger = logging.getLogger(__name__)

class BackendAPI:
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")

    async def _request(self, method: str, path: str, json: dict | None = None, timeout_sec: int = 8):
        url = f"{self.base}{path}"
        timeout = aiohttp.ClientTimeout(total=timeout_sec)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if method == "get":
                    async with session.get(url) as resp:
                        text = await resp.text()
                        try:
                            data = await resp.json()
                        except Exception:
                            logger.error("Invalid JSON from backend %s: %s", url, text)
                            return resp.status, None
                        return resp.status, data
                else:
                    async with session.post(url, json=json) as resp:
                        text = await resp.text()
                        try:
                            data = await resp.json()
                        except Exception:
                            logger.error("Invalid JSON from backend %s: %s", url, text)
                            return resp.status, None
                        return resp.status, data
        except asyncio.TimeoutError:
            logger.exception("Timeout when contacting backend %s", url)
            return None, None
        except Exception:
            logger.exception("Error when contacting backend %s", url)
            return None, None

    async def get(self, path: str):
        return await self._request("get", path)

    async def post(self, path: str, payload: dict):
        return await self._request("post", path, json=payload)


backend_api = BackendAPI(BACKEND_URL)
