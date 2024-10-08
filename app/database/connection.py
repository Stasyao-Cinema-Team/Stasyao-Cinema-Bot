from os import getenv
from typing import Optional, Type, List
from types import TracebackType
from contextlib import contextmanager

from sqlalchemy import *
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.models import *
from app.logger.logger import Logger

logger = Logger()


class Database:
    __instance: "Type[Database] | None" = None
    __initialised: bool = False

    __path: str
    __engine: Engine
    __sessionmaker: sessionmaker

    @logger.time_it_info(description="Initialise database connection")
    def __init__(self) -> None:
        if not self.__initialised:
            self.__path = getenv("DB_PATH", "prod.db")
            self.__engine = self.__create_engine(path=self.__path)
            self.__sessionmaker = self.__create_sessionmaker(engine=self.__engine)
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
        self.__engine.dispose()
        return False

    def get_engine(self) -> Engine:
        return self.__engine

    def get_sessionmaker(self) -> sessionmaker:
        return self.__sessionmaker

    def get_session(self) -> Session:
        return self.__sessionmaker()

    @contextmanager
    def context_cursor(self) -> Session:
        with self.get_session() as session:
            try:
                yield session
            except Exception as e:
                session.rollback()
                logger.exception(e)
            else:
                session.commit()
            finally:
                session.close()

    @staticmethod
    @logger.time_it_debug(description="Create database engine")
    def __create_engine(path) -> Engine:
        return create_engine(
            url=f"sqlite:///{path}",
            hide_parameters=False,
            poolclass=StaticPool,
            echo=True if getenv("LOG_LEVEL") else False,
        )

    @staticmethod
    @logger.time_it_debug(description="Create database session")
    def __create_sessionmaker(engine: Engine) -> sessionmaker:
        return sessionmaker(
            bind=engine,
            expire_on_commit=False,
        )


def cast_data(data: List[Row]):
    if len(data) == 0:
        return []
    result = []
    for row in data:
        if isinstance(row, Row):
            result.append(row[0])
    return result
