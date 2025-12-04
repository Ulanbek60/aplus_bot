# services/user_service.py

from services.api_client import backend_api


class UserService:
    async def full_register(self, **data):
        """
        Полная регистрация водителя/механика.
        Отправляет все данные на /full_register/.
        """
        status, response = await backend_api.post("/api/users/full_register/", data)
        return status, response

    async def get_profile(self, telegram_id: int):
        """
        Получение полного профиля пользователя.
        """
        status, data = await backend_api.get(f"/api/users/profile/{telegram_id}/")
        return status, data

    async def request_vehicle(self, telegram_id: int, vehicle_id: str):
        """
        Отправка заявки на выбор техники водителем.
        """
        payload = {
            "telegram_id": telegram_id,
            "vehicle_id": vehicle_id
        }
        status, data = await backend_api.post("/api/users/request_vehicle/", payload)
        return status, data

    async def approve_vehicle(self, telegram_id: int, vehicle_id: str):
        """
        Подтверждение техники администратором (если нужно из бота).
        Обычно вызывается с админки.
        """
        payload = {
            "telegram_id": telegram_id,
            "vehicle_id": vehicle_id
        }
        status, data = await backend_api.post("/api/users/approve_vehicle/", payload)
        return status, data


# глобальный экземпляр
user_service = UserService()
