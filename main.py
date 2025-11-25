import asyncio
from app import create_app

async def main():
    print('Запуск бота...')
    bot, dp = await create_app()
    # Запуск polling — передаём экземпляр bot
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
