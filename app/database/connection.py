from contextlib import contextmanager
from os import getenv
from os.path import isdir
from os.path import isfile
from types import TracebackType
from typing import List
from typing import Optional
from typing import Type

from sqlalchemy import create_engine
from sqlalchemy import Engine
from sqlalchemy import select  # noqa: F401
from sqlalchemy import insert  # noqa: F401
from sqlalchemy import update  # noqa: F401
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.models import Actions  # noqa: F401
from app.database.models import Admins  # noqa: F401
from app.database.models import Data  # noqa: F401
from app.database.models import Events  # noqa: F401
from app.database.models import Ordering  # noqa: F401
from app.database.models import Users  # noqa: F401
from app.logger.logger import Logger

logger = Logger()


class Database:
    __instance: "Type[Database] | None" = None
    __initialised: bool = False

    __path: str
    __engine: Engine
    __sessionmaker: sessionmaker

    def __init__(self) -> None:
        if not self.__initialised:
            self.__init()

    @logger.time_it_info(description="Initialise database connection")
    def __init(self):
        DB_PATH = getenv("DB_PATH")
        if not DB_PATH:
            logger.warn("\"DB_PATH\" environment variable not set. Use default value \"prod.db\"")
            DB_PATH = "prod.db"
        if not isfile(DB_PATH):
            logger.info(f"Creating new database file at \"{DB_PATH}\"")
            open(DB_PATH, "w+").close()
        if not isfile(DB_PATH) or isdir(DB_PATH):
            raise IOError(f"File \"{DB_PATH}\" does not exist or it is a directory")
        self.__path = DB_PATH
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
