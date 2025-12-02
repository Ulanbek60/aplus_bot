import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")

FAKE_BACKEND = os.getenv("FAKE_BACKEND", "False").lower() == "true"

REDIS_URL = os.getenv("REDIS_URL")
APP_ENV = os.getenv("APP_ENV", "production")

PILOT_API_URL = os.getenv("PILOT_API_URL")
PILOT_LOGIN = os.getenv("PILOT_LOGIN")
TASK_API_URL = os.getenv("TASK_API_URL")


