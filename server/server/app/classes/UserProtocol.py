import json
import time
from uuid import uuid4
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from common.events import EventHandler
from common.packets import BasePacket, MessagePacket
from server.app.classes.UserInfo import UserInfo
from server.app.classes.enums import UserState, UserJoinState


class UserProtocol(Protocol):

    def __init__(self, server) -> None:
        """
        Initializes a new UserProtocol instance.

        Args:
            server (Server): Reference to the server instance.
        """
        from server.app.factory import ServerFactory as Server

        self.state = UserJoinState.JOINING
        self.motd = "Welcome to the chat server! The first message you send will be your username!"
        self.server: Server = server
        self.info = UserInfo(uuid4(), None)
        self.events = EventHandler()
        self.events.on("Connection.Made", self.server.users.addUser)
        if self.server.debug:
            self.events.on("all", self.debug)

    def debug(self, *args, **kwargs):

        print(f"[{self.info.id}] {args} {kwargs}")

    def dataReceived(self, data: bytes) -> None:
        """
        Receives data from the connected user and broadcasts it to all users.

        Args:
            data (bytes): The data received from the user.
        """
        packet = BasePacket.decode(data)

        if packet:
            self.events.emit(f"Recv.{packet.type}", packet)

    def connectionMade(self) -> None:
        """
        Called when a new connection is established.

        Registers the user with the server's UserRegistry.
        """
        self.events.emit("Connection.Made", self)

    def connectionLost(self, reason: str) -> None:
        """
        Called when the connection is lost.

        Currently empty, but can be implemented to handle cleanup tasks.

        Args:
            reason (str): Reason for the connection loss.
        """
        self.events.emit("Connection.Lost")

    def send(self, data: bytes | BasePacket) -> None:
        """
        Sends data to the connected user over the network.

        Args:
            data (bytes): The data to send.
        """
        if issubclass(data.__class__, BasePacket):
            data = data.prep()
        packet = BasePacket.decode(data)
        self.events.emit(f"Send.{packet.type}", packet)
        self.transport.write(data)

    def __str__(self) -> str:
        return f"<UserProtocol {self.info.id}>"

    def __repr__(self) -> str:
        return f"<UserProtocol {self.info.id}>"
