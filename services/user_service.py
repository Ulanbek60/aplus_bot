# services/user_service.py
from services.api_client import backend_api

class UserService:
    async def get_profile(self, telegram_id: int):
        status, data = await backend_api.get(f"/api/users/profile/{telegram_id}/")
        return status, data

    async def register_user(self, telegram_id: int, phone: str, name: str, surname: str, language: str):
        payload = {
            "telegram_id": telegram_id,
            "phone": phone,
            "name": name,
            "surname": surname,
            "language": language,
        }
        status, data = await backend_api.post("/api/users/register/", payload)
        return status, data

    async def request_vehicle(self, telegram_id: int, vehicle_id: int):
        payload = {"telegram_id": telegram_id, "vehicle_id": vehicle_id}
        status, data = await backend_api.post("/api/users/request_vehicle/", payload)
        return status, data

user_service = UserService()