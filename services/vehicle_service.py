from services.api_client import backend_api


class VehicleService:
    async def get_vehicle_list(self):
        status, data = await backend_api.get("/api/vehicles/list/")
        return status, data


vehicle_service = VehicleService()
