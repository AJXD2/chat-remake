from pathlib import Path
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from server.app.factory import ServerFactory
import configparser
from rich.logging import RichHandler
from rich.console import Console
import logging

BASE = Path(__file__).absolute().parent
console = Console()

logging.basicConfig(
    level=logging.INFO,  # Set the logging level as needed
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console)],
)


def main():
    config = configparser.ConfigParser()
    config.read(BASE.joinpath("config.ini"))
    logging.info(
        "Starting server on {IP}:{PORT}".format(
            IP=config.get("Server", "ip"), PORT=config.get("Server", "port")
        )
    )
    endpoint = TCP4ServerEndpoint(reactor, 2000)
    endpoint.listen(ServerFactory(config))
    reactor.run()


if __name__ == "__main__":
    main()

# something
