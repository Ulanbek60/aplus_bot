from .api_client import api_client

class UserService:
    async def register_user(self, telegram_id, phone, name, surname, language):
        payload = {
            "telegram_id": telegram_id,
            "phone": phone,
            "name": name,
            "surname": surname,
            "language": language
        }

        status, data = await api_client.post("/api/users/register/", payload)
        return status, data

    async def request_vehicle(self, telegram_id, vehicle_id):
        payload = {
            "telegram_id": telegram_id,
            "vehicle_id": vehicle_id
        }

        status, data = await api_client.post("/api/users/request_vehicle/", payload)
        return status, data


user_service = UserService()
