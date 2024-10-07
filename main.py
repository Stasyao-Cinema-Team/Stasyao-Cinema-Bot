from asyncio import run

from app.logger.logger import Logger
from app import Server


logger = Logger()


async def main():
    """
    Entrypoint function
    """
    server = Server()
    await server.start_server()(server.get_bot())


if __name__ == "__main__":
    try:
        logger.info("Startup.")
        run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutdown.")
    except Exception as e:
        logger.exception(e)
