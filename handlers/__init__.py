from .start import router as start_router
from .fuel import router as fuel_router
from .shift import router as shift_router
from .issue import router as issue_router
from .fallback import router as fallback_router
from .auth import router as auth_router
from .profile import router as profile_router


def register_all_handlers(dp):
    dp.include_router(start_router)
    dp.include_router(auth_router)
    dp.include_router(fuel_router)
    dp.include_router(shift_router)
    dp.include_router(issue_router)
    dp.include_router(fallback_router)
    dp.include_router(profile_router)
