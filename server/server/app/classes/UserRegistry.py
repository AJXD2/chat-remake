from typing import Callable, Dict, List
from uuid import uuid4
from twisted.internet.protocol import Protocol
from server.app.classes.UserProtocol import UserProtocol
from server.app.classes.UserInfo import UserInfo
from server.app.classes.enums import UserState, UserJoinState
from server.app.classes.PrecheckResponse import PrecheckResponse
from common.packets import BasePacket, KickPacket, MessagePacket
import json
from common.events import EventHandler

# from time import sleep


class UserRegistry:

    def __init__(self) -> None:
        """
        Initializes a new UserRegistry instance.

        Manages a list of connected users.
        """
        self.users: List[UserProtocol] = []
        self.prechecks = EventHandler().on("Precheck.Join", self.check_username)

    @property
    def online(self):
        """
        Returns a list of online users.

        Returns:
            List[UserProtocol]: The online users.
        """

        return [u for u in self.users if u.transport.connected]

    @property
    def online_count(self):
        """
        Returns the number of online users.

        Returns:
            int: The number of online users.
        """

        return len(self.online)

    def check_username(self, user: UserProtocol) -> PrecheckResponse:
        """
        Checks if a username is already in use.

        Args:
            user (UserProtocol): The user to check.

        Returns:
            PrecheckResponse: Whether the username is available.
        """

        if user.info.username in [u.info.username for u in self.users]:
            raise PrecheckResponse(
                False, f"Username {user.info.username} is already in use."
            )
        return PrecheckResponse(True)

    def addUser(self, user: UserProtocol) -> None:
        """
        Adds a user to the registry.

        Args:
            user (UserProtocol): The user to add.
        """
        try:
            self.prechecks.emit("Precheck.Join", user)
            self.users.append(user)
        except PrecheckResponse as e:
            user.transport.write(KickPacket(e.reason).prep())
            user.transport.loseConnection()

    def getUser(self, id_: str | UserProtocol) -> UserProtocol | None:
        """
        Retrieves a user by ID or UserProtocol object.

        Args:
            id_ (str | UserProtocol): The user ID (string) or the UserProtocol object itself.

        Returns:
            UserProtocol: The UserProtocol object if found, otherwise None.
        """
        if isinstance(id_, UserProtocol):
            return id_
        for user in self.users:
            if user.info.id == id_:
                return user
        return None

    def removeUser(self, id_: UserProtocol | str) -> None:
        """
        Removes a user from the registry.

        Args:
            id_ (UserProtocol | str): The user ID (string) or the UserProtocol object itself.
        """
        user = self.getUser(id_)
        try:
            if user:
                self.users.remove(user)
        except ValueError:
            pass

    def kick_user(self, id_: UserProtocol | str, reason: str = None) -> None:
        """
        Kicks a user from the server.

        Args:
            id_ (UserProtocol | str): The user ID (string) or the UserProtocol object itself.
        """
        user = self.getUser(id_)
        if user:
            if reason is None:
                reason = "No reason specified."
            self.removeUser(user)
            user.send(
                KickPacket(
                    {
                        "reason": reason,
                    }
                )
            )

            user.transport.loseConnection()

    def pack_packet(self, data: str | bytes | dict | BasePacket) -> bytes:
        """
        Packs data into a packet.

        Handles different data types (bytes, strings, or dictionaries).

        Args:
            data (str | bytes | dict | BasePacket): The data to pack.

        Returns:
            bytes: The packed data.
        """

        if isinstance(data, dict):
            data = json.dumps(data).encode()
        elif isinstance(data, str):
            data = data.encode()
        else:
            if issubclass(data.__class__, BasePacket):
                data = data.prep()
        return data

    def broadcast(self, data: str | bytes | dict) -> None:
        """
        Broadcasts data to all connected users.

        Args:
            data (str | bytes | dict): The data to broadcast.
        """
        data = self.pack_packet(data)

        for user in self.users:
            self.send_to(data, user)

    def send_to(self, data: str | bytes | dict, who: str | UserProtocol) -> None:
        """
        Sends data to a specific user.

        Handles different data types (bytes, strings, or dictionaries).

        Args:
            data (str | bytes | dict): The data to send.
            who (str | UserProtocol): The user ID (string) or the UserProtocol object to send to.
        """
        data = self.pack_packet(data)

        user = self.getUser(who)
        if user:
            user.send(data)
