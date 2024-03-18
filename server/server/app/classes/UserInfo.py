from dataclasses import dataclass


@dataclass
class UserInfo:
    """
    Holds information about a user.
    """

    id: str | bytes
    """Unique identifier for the user."""
    username: str
    """Username of the user."""
    auth: None = None
    """Optional field for authentication details (not currently used)."""
