from .api_client import api_client

class VehicleService:
    async def get_vehicle_list(self):
        status, data = await api_client.get("/api/vehicles/list/")
        return status, data


vehicle_service = VehicleService()
