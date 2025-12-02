# services/user_service.py
from services.api_client import backend_api


class UserService:
    async def register_user(self, telegram_id, phone, name, surname, language):
        payload = {
            "telegram_id": telegram_id,
            "phone": phone,
            "name": name,
            "surname": surname,
            "language": language
        }
        return await backend_api.post("/api/users/register/", payload)

    async def request_vehicle(self, telegram_id, vehicle_id):
        payload = {
            "telegram_id": telegram_id,
            "vehicle_id": vehicle_id
        }
        return await backend_api.post("/api/users/request_vehicle/", payload)

    async def get_profile(self, telegram_id):
        return await backend_api.get(f"/api/users/profile/{telegram_id}/")


# ВОТ ЭТО ВАЖНО
user_service = UserService()
