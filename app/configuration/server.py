from os import getenv
from typing import Type # noqa: F401

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import BaseStorage
from aiogram_sqlite_storage.sqlitestore import SQLStorage

from app.handlers import __handlers__
from app.logger.logger import Logger

logger = Logger()


class Server:
    """
    Server class to initialise Aiogram Bot server.
    """

    __instance: "Type[Server] | None" = None
    __initialised: bool = False

    __title = "Stasyao Cinema Bot"
    __version = "0.1.0"
    __bot: Bot
    __storage: BaseStorage
    __dispatcher: Dispatcher

    @logger.time_it_info(description="Server initialising")
    def __init__(self) -> None:
        if not self.__initialised:
            TOKEN = getenv("TOKEN")
            if not TOKEN:
                raise KeyError('TOKEN environment variable not set')
            self.__bot = self.__prepeare_bot(
                token=TOKEN
            )
            self.__storage = self.__prepeare_storage()
            self.__dispatcher = self.__prepeare_dispatcher(
                bot=self.__bot, storage=self.__storage
            )
            self.__register_handlers(dispatcher=self.__dispatcher)
            self.__initialised = True

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super(Server, cls).__new__(cls)
        return cls.__instance

    def get_bot_dispatcher(self):
        """
        Get method to return Server dispatcher class.
        :return: aiogram.Dispatcher class
        """
        return self.__dispatcher

    def get_bot(self):
        """
        Get method to return Server bot class.
        :return: aiogram.Bot class
        """
        return self.__bot

    def get_title(self):
        """
        Get method to return Server title.
        :return: Server.title
        """
        return self.__title

    def get_version(self):
        """
        Get method to return Server version.
        :return: Server.version
        """
        return self.__version

    def start_server(self):
        """
        Start function for Polling runner
        :return: Coroutine
        """
        return self.get_bot_dispatcher().start_polling

    @staticmethod
    @logger.time_it_debug(description="Prepearing aiogram.Bot server's instance")
    def __prepeare_bot(token: str) -> Bot:
        return Bot(token=token, default=DefaultBotProperties(parse_mode="Markdown"))

    @staticmethod
    @logger.time_it_debug(
        description="Prepearing aiogram_sqlite_storage.sqlitestore.SQLStorage server's instance"
    )
    def __prepeare_storage() -> BaseStorage:
        return SQLStorage()

    @staticmethod
    @logger.time_it_debug(description="Prepearing aiogram.Dispatcher server's instance")
    def __prepeare_dispatcher(bot: Bot, storage: BaseStorage) -> Dispatcher:
        return Dispatcher(bot=bot, storage=storage)

    @staticmethod
    @logger.time_it_debug(description="Registering server's handlers")
    def __register_handlers(dispatcher: Dispatcher):
        __handlers__.register_routes(dispatcher=dispatcher)
