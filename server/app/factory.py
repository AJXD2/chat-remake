from configparser import ConfigParser
from pathlib import Path
from common.events import EventHandler
from app.classes.UserRegistry import UserRegistry
from app.classes.UserProtocol import UserProtocol
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ServerFactory as ServFactory
import os
from rich.console import Console
from rich.logging import RichHandler
import logging


# Create a console object for rich logging
console = Console()

BASE = Path(__file__).parent.parent

# Configure logging with rich handler
logger = logging.getLogger("Server")


class ServerFactory(ServFactory):
    def __init__(self, config: ConfigParser) -> None:
        self.users = UserRegistry(self)

        self.events = EventHandler()
        self.base = BASE
        self.config = config
        self.debug = config.getboolean("Server", "debug")
        if self.debug:
            logger.setLevel(logging.DEBUG)
            logger.debug("[green bold]Debugging mode enabled.[/]")

        logger.info("Server starting.")

    def buildProtocol(self, addr) -> Protocol:
        return UserProtocol(self)
