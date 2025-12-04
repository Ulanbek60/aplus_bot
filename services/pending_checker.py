import asyncio
from locales.i18n import USER_LANG, MESSAGES
from keyboards import main_menu
from services.user_service import user_service
from services.state import PENDING_USERS

async def pending_checker(bot, PENDING_USERS):
    while True:
        for uid in list(PENDING_USERS):
            status, profile = await user_service.get_profile(uid)
            if profile and profile.get("status") == "active":
                PENDING_USERS.remove(uid)

                lang = profile.get("language", "ru")
                USER_LANG[uid] = lang

                await bot.send_message(uid, MESSAGES[lang]["vehicle_approved"])
                await bot.send_message(uid, MESSAGES[lang]["menu"], reply_markup=main_menu(MESSAGES[lang]))

        await asyncio.sleep(8)
