from dataclasses import dataclass
from typing import Tuple

from aiogram import Dispatcher, Router

from app.logger.logger import Logger

from .user import router as user_router
from .admin import router as admin_router

logger = Logger()


@dataclass(frozen=True)
class Handlers:
    """
    Basic Handlers class.
    To initialise ur handler add it below.
    """

    routers: Tuple[Router]

    def register_routes(self, dispatcher: Dispatcher):
        """
        Register all given routes function.
        """

        for router in self.routers:
            logger.debug(f"Registering handler's {router.name} router.")
            dispatcher.include_router(router)


__handlers__ = Handlers(
    routers=(
        user_router,
        admin_router,
    )
)
