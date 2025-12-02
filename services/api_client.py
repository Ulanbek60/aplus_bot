# services/api_client.py
import aiohttp
from config import BACKEND_URL
import logging

logger = logging.getLogger(__name__)


class BackendAPI:
    def __init__(self):
        self.base_url = BACKEND_URL.rstrip("/")

    async def _request(self, method: str, endpoint: str, json=None):
        url = f"{self.base_url}{endpoint}"

        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(method, url, json=json) as resp:
                    text = await resp.text()

                    if resp.status >= 400:
                        logger.error(f"Backend error {resp.status}: {text}")
                        return None

                    try:
                        return await resp.json()
                    except:
                        logger.error(f"Invalid JSON: {text}")
                        return None

        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None

    # ----------------------------------------------------------------------
    # AUTH / REGISTRATION
    # ----------------------------------------------------------------------

    async def register_user(self, tg_id: int, name: str, phone: str):
        """
        POST /api/users/register/
        """
        payload = {
            "tg_id": tg_id,
            "name": name,
            "phone": phone
        }
        return await self._request("POST", "/api/users/register/", json=payload)

    async def update_lang(self, tg_id: int, lang: str):
        """
        POST /api/users/update_lang/
        """
        payload = {"tg_id": tg_id, "lang": lang}
        return await self._request("POST", "/api/users/update_lang/", json=payload)

    async def get_profile(self, tg_id: int):
        """
        GET /api/users/profile/<tg_id>/
        """
        return await self._request("GET", f"/api/users/profile/{tg_id}/")

    # ----------------------------------------------------------------------
    # VEHICLES (Incomtek)
    # ----------------------------------------------------------------------

    async def get_vehicle_list(self):
        """
        GET /api/vehicles/list/
        """
        return await self._request("GET", "/api/vehicles/list/")

    async def request_vehicle(self, tg_id: int, vehicle_id: int):
        """
        POST /api/users/request_vehicle/
        """
        payload = {
            "tg_id": tg_id,
            "vehicle_id": vehicle_id
        }
        return await self._request("POST", "/api/users/request_vehicle/", json=payload)


# создаём один глобальный клиент
backend_api = BackendAPI()
