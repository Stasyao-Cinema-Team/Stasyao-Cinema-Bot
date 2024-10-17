from asyncio import run, get_event_loop, gather

from app.configuration.server import Server
from app.flet.app import start
from app.logger.logger import Logger

logger = Logger()


async def bot():
    """
    Entrypoint bot function
    """
    server = Server()
    await server.start_server()(server.get_bot())


async def web():
    """
    Entrypoint web function
    """
    await start(port=8080)


async def main():
    """
    Entrypoint web function
    """
    modules = [
        bot(),
        web()
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
