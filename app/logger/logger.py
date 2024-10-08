"""
Base Logger module.
"""

import os
import sys
from inspect import getmodule
from logging import INFO, NOTSET, FileHandler
from logging import Filter as DefaultFilter
from logging import Formatter
from logging import Logger as DefaultLogger
from logging import LogRecord, StreamHandler, getLogger
from time import perf_counter_ns
from functools import wraps

try:
    from colorlog import ColoredFormatter

    colored = True
except ImportError:
    from logging import Formatter as ColoredFormatter

    colored = False


def currentframe():
    """
    Return the frame object for the caller's stack frame.
    """
    if hasattr(sys, "_getframe"):
        return sys._getframe(1).f_back
    else:
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[2].tb_frame.f_back.f_back[
                0
            ]  # pyright: ignore[reportOptionalMemberAccess,reportIndexIssue,reportOptionalSubscript]


class Logger:
    """
    Basic Logger class.
    """

    _log_settings = {}
    _logger: DefaultLogger
    _file_handler = None
    _stream_handler = None
    _log_format = (
        "| %(relativeCreated)5d "
        "| %(asctime)s "
        "| %(log_color)s%(levelname)8s%(reset)s "
        "| %(threadName)s [%(process)d] "
        "| %(special_name)s "
        "|\n%(message)s"
    )

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_logger") or cls._logger is None:

            class ExtraFileNameDefault(DefaultFilter):
                """
                Set file path from root by default without extra={'special_name': __name__}
                """

                def filter(self, record: LogRecord):
                    if not hasattr(record, "special_name"):
                        # Black Magic
                        _stack = (
                            currentframe().f_back.f_back.f_back.f_back
                        )  # pyright: ignore[reportOptionalMemberAccess]
                        _module_name = getmodule(
                            _stack
                        ).__name__  # pyright: ignore[reportOptionalMemberAccess]
                        _fun_name = (
                            _stack.f_code.co_name
                        )  # pyright: ignore[reportOptionalMemberAccess]
                        record.special_name = f"{_module_name}.{_fun_name}"
                    return super().filter(record)

            class RelativeCreatedInSec(DefaultFilter):
                """
                Set relativeCreated data in seconds instead of milliseconds.
                """

                def filter(self, record: LogRecord) -> bool | LogRecord:
                    record.relativeCreated = record.relativeCreated // 1000
                    return super().filter(record)

            def fix_libs_logger(libs):
                for lib in libs:
                    target_lib = getLogger(lib)
                    target_lib.addFilter(ExtraFileNameDefault())
                    target_lib.addFilter(RelativeCreatedInSec())

            cls._logger = super().__new__(
                cls, *args, **kwargs
            )  # pyright: ignore[reportAttributeAccessIssue]
            _fix_libs = [
                "requests",
                "urllib3",
                "urllib3.connectionpool",
                "sqlalchemy",
                "sqlalchemy.engine.Engine",
                "sqlalchemy.pool.impl.AsyncAdaptedQueuePool",
                "aiogram_sqlite_storage.sqlitestore",
                "asyncio",
                "aiosqlite",
                "aiogram",
                "aiogram.dispatcher",
                "aiogram.event",
                "aiogram.middlewares",
                "aiogram.webhook",
                "aiogram.scene",
            ]
            fix_libs_logger(_fix_libs)
            cls._logger = getLogger("root")
            cls._logger.addFilter(ExtraFileNameDefault())
            cls._logger.addFilter(RelativeCreatedInSec())
            cls._logger.root.setLevel(level=NOTSET)

            # File log handler.
            cls._file_handler = FileHandler("app.log")
            cls._file_handler.setLevel(INFO)
            cls._file_handler.setFormatter(
                Formatter(
                    cls._log_format.replace("%(log_color)s", "").replace(
                        "%(reset)s", ""
                    )
                )
            )

            # Stream log handler.
            cls._stream_handler = StreamHandler()
            cls._stream_handler.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
            cls._stream_handler.setFormatter(
                ColoredFormatter(
                    cls._log_format
                    if colored
                    else cls._log_format.replace("%(log_color)s", "").replace(
                        "%(reset)s", ""
                    )
                )
            )

            cls._logger.addHandler(cls._file_handler)
            cls._logger.addHandler(cls._stream_handler)

            def time_it_info(_func=None, description="[Missed time_it description]"):
                def _time_it_info(func):
                    @wraps(func)
                    def wrapper(*args, **kwargs):
                        cls._logger.info(
                            f"{description} started.",
                            extra={
                                "special_name": f"{func.__module__}.{func.__name__}"
                            },
                        )
                        __timer_start = perf_counter_ns()
                        response = func(*args, **kwargs)
                        __timer_end = perf_counter_ns()
                        cls._logger.info(
                            f"{description} is done. ({(__timer_end - __timer_start) / 1_000_000:.4f} ms)",
                            extra={
                                "special_name": f"{func.__module__}.{func.__name__}"
                            },
                        )
                        return response

                    return wrapper

                if _func is None:
                    return _time_it_info
                return _time_it_info(_func)

            cls._logger.time_it_info = time_it_info

            def time_it_debug(_func=None, description="[Missed time_it description]"):
                def _time_it_debug(func):
                    @wraps(func)
                    def wrapper(*args, **kwargs):
                        args_repr = [repr(a) for a in args]
                        kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
                        variables = ", ".join(args_repr + kwargs_repr)
                        cls._logger.debug(
                            f"{description} started.{' [' + variables + ']' if variables else ''}",
                            extra={
                                "special_name": f"{func.__module__}.{func.__name__}"
                            },
                        )
                        __timer_start = perf_counter_ns()
                        response = func(*args, **kwargs)
                        __timer_end = perf_counter_ns()
                        cls._logger.debug(
                            f"{description} is done. {'[' + response.__str__() + '] ' if response else ''}({(__timer_end - __timer_start) / 1_000_000:.4f} ms)",
                            extra={
                                "special_name": f"{func.__module__}.{func.__name__}"
                            },
                        )
                        return response

                    return wrapper

                if _func is None:
                    return _time_it_debug
                return _time_it_debug(_func)

            cls._logger.time_it_debug = time_it_debug

        return cls._logger
