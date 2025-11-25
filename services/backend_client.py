import aiohttp
from config import BACKEND_URL, FAKE_BACKEND

async def send_event(event_type: str, payload: dict):

    # фейковый backend
    if FAKE_BACKEND:
        if event_type == "auth":
            return {"authorized": True, "role": "driver"}

        if event_type == "fuel":
            return {"status": "ok"}

        if event_type == "issue":
            return {"status": "ok"}

        if event_type == "shift":
            return {"saved": True}

        return {"ok": True}

    # реальный backend
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


# here is real backend
# async def send_event(event_type: str, payload: dict):
#     data = {'event': event_type, 'data': payload}
#     timeout = aiohttp.ClientTimeout(total=10)
#     async with aiohttp.ClientSession(timeout=timeout) as session:
#         async with session.post(BACKEND_URL, json=data) as resp:
#             text = await resp.text()
#             if resp.status >= 400:
#                 raise Exception(f"Backend error: {resp.status} {text}")
#             try:
#                 return await resp.json()
#             except Exception:
#                 return text
#