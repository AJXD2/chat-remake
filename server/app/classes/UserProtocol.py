import json
import logging
import time
from uuid import uuid4
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from common.events import EventHandler
from common.packets import BasePacket, MessagePacket
from app.classes.UserInfo import UserInfo
from app.classes.enums import UserState, UserJoinState

logger = logging.getLogger("Server")


class UserProtocol(Protocol):

    def __init__(self, server) -> None:
        """
        Initializes a new UserProtocol instance.

        Args:
            server (Server): Reference to the server instance.
        """
        from app.factory import ServerFactory as Server

        self.server: Server = server

        self.motd = server.config.get("General", "motd")
        self.info = UserInfo(uuid4(), None)
        self.events = server.events
        self.server.events.on("Connection.Made", self.server.users.addUser)
        if self.server.debug:
            self.server.events.on("*", self.debug)

    def debug(self, *args, **kwargs):

        logger.debug(f"[{self.info.id}] {args} {kwargs}")

    def dataReceived(self, data: bytes) -> None:
        """
        Receives data from the connected user and broadcasts it to all users.

        Args:
            data (bytes): The data received from the user.
        """
        packet = BasePacket.decode(data)

        if packet:
            self.server.events.emit(f"Recv.{packet.type}", packet)

    def connectionMade(self) -> None:
        """
        Called when a new connection is established.

        Registers the user with the server's UserRegistry.
        """
        self.server.events.emit("Connection.Made", self)

    def connectionLost(self, reason: str) -> None:
        """
        Called when the connection is lost.

        Currently empty, but can be implemented to handle cleanup tasks.

        Args:
            reason (str): Reason for the connection loss.
        """
        self.server.events.emit("Connection.Lost", self)

    def send(self, data: bytes | BasePacket) -> None:
        """
        Sends data to the connected user over the network.

        Args:
            data (bytes): The data to send.
        """
        if issubclass(data.__class__, BasePacket):
            data = data.prep()
        packet = BasePacket.decode(data)
        self.server.events.emit(f"Send.{packet.type}", packet)
        self.transport.write(data)

    def __str__(self) -> str:
        return f"<UserProtocol {self.info.id}>"

    def __repr__(self) -> str:
        return f"<UserProtocol {self.info.id}>"
