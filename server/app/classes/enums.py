from enum import Enum


class UserState(Enum):
    """
    Represents the state of a user.
    """

    ONLINE = 1
    OFFLINE = 2
    AFK = 3
    BANNED = 4


class UserJoinState(Enum):
    """
    Represents the state of a user when joining a channel.
    """

    JOIN_FAILED = -1
    JOINING = 1
    USERNAME = 2
    # PASSWORD = 3
    JOINED = 4
