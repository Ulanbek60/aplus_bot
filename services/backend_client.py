import aiohttp
from config import BACKEND_URL

async def send_event(event_type: str, payload: dict):
    data = {'event': event_type, 'data': payload}
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(BACKEND_URL, json=data) as resp:
            text = await resp.text()
            if resp.status >= 400:
                raise Exception(f"Backend error: {resp.status} {text}")
            try:
                return await resp.json()
            except Exception:
                return text
