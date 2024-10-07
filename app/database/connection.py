from os import getenv
from typing import Optional, Type, List
from types import TracebackType
from contextlib import contextmanager

from sqlalchemy import *
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import Session

from app.database.models import *
from app.logger.logger import Logger

logger = Logger()


class Database:
    __instance: "Type[Database] | None" = None
    __initialised: bool = False

    __path: str
    __engine: Engine
    __connection: Connection

    @logger.time_it_info(description="Initialise database connection")
    def __init__(self) -> None:
        if not self.__initialised:
            self.__path = getenv("DB_PATH", "local.db")
            self.__engine = self.__create_engine(path=self.__path)
            self.__connection = self.__create_connection(engine=self.__engine)
            self.__initialised = True

    def __new__(self, *args, **kwargs):
        if not self.__instance:
            self.__instance = super().__new__(self, *args, **kwargs)
        return self.__instance

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType],
    ) -> bool:
        self.__connection.close()
        return False

    def get_connection(self) -> Connection:
        return self.__connection

    @contextmanager
    def context_cursor(self) -> Session:
        connection = self.get_connection()
        with Session(connection, expire_on_commit=False) as session:
            try:
                yield session
            except Exception as e:
                session.rollback()
                logger.exception(e)
            else:
                session.commit()

    @staticmethod
    @logger.time_it_debug(description="Connect to database")
    def __create_engine(path) -> Engine:
        return create_engine(
            url=f"sqlite:///{path}",
            hide_parameters=False,
            poolclass=SingletonThreadPool,
            future=True,
            echo=True,
        )

    @staticmethod
    @logger.time_it_debug(description="Connect to database")
    def __create_connection(engine) -> Connection:
        return engine.connect()


def cast_data(data: List[Row]):
    if len(data) == 0:
        return []
    result = []
    for row in data:
        if isinstance(row, Row):
            result.append(row[0])
    return result
