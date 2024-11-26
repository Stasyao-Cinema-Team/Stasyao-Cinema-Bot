from asyncio import gather
from asyncio import get_event_loop
from asyncio import run

from app.configuration.server import Server
from app.flet.flet_app import start
from app.logger.logger import Logger

logger = Logger()


async def bot():
    """
    Entrypoint bot function
    """
    server = Server()
    await server.start_server()(server.get_bot())


def web():
    """
    Entrypoint web function
    """
    return start()


async def main():
    """
    Entrypoint web function
    """
    modules = [
        web(),
        bot(),
    ]
    await gather(*modules)


if __name__ == "__main__":
    try:
        logger.info("Startup.")
        run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutdown.")
    except Exception as e:
        logger.exception(e)
