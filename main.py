import asyncio
from app import create_app, PENDING_USERS
from services.pending_checker import pending_checker
from services.state import PENDING_USERS

async def main():
    print('Запуск бота...')
    bot, dp = await create_app()

    asyncio.create_task(pending_checker(bot, PENDING_USERS))

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
