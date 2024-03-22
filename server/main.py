import logging
import configparser
from pathlib import Path
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from app.factory import ServerFactory
from rich.logging import RichHandler
from rich.console import Console

BASE = Path(__file__).absolute().parent
console = Console()


def init_logger():
    logger = logging.getLogger("Server")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[[cyan bold]%(threadName)s[/]] %(message)s", datefmt="[%X]"
    )

    rh = RichHandler(console=console, markup=True)
    rh.setFormatter(formatter)

    logger.addHandler(rh)
    return logger


def main(reactor=reactor):
    config = configparser.ConfigParser()
    config.read(BASE.joinpath("config.ini"))

    logger = init_logger()
    factory = ServerFactory(config)
    endpoint = TCP4ServerEndpoint(reactor, config.getint("Server", "port"))

    d = endpoint.listen(factory)
    d.addCallback(
        lambda port: logger.info(
            f"Starting server on {config.get('Server', 'ip')}:{port.getHost().port}"
        )
    )
    reactor.run()


if __name__ == "__main__":
    main()
