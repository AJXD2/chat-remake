import json
from typing import Union


class VerificationError(Exception):
    pass


class BasePacket(object):
    """Base of all Packet types.

    Args:
        data (dict): The data to send.

    .. highlight:: python
    .. code-block:: python

        class OtherPacket(BasePacket):
            def verify(self):
                # Verification code here
                verified = False
                if verified:
                    return True

                return False

    Raises:
        VerificationError: If verification of packet failed.
        NotImplementedError: If the subclass does not implement the verify method.

    """

    subclasses = {}
    extra_prep = []

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        cls.subclasses[cls.__name__] = cls

    def __init__(self, data):
        self.data = data

    def prep(self):
        print(self.data)
        self.data["type"] = self.get_type()
        for i in self.extra_prep:
            i()
        if self.verify():

            return json.dumps(self.data).encode()
        else:
            raise VerificationError(f"'{self.__class__.__name__}' Failed verification.")

    def verify(self):
        raise NotImplementedError("Must be implemented by subclass")

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.data}>"

    @property
    def type(self):
        return self.get_type()

    @classmethod
    def decode(cls, data: bytes) -> Union["BasePacket", "MessagePacket", None]:

        try:
            data = json.loads(data.decode())
            return cls.subclasses[data.get("type")](data)
        except (KeyError, AssertionError, json.JSONDecodeError):
            return None

    @classmethod
    def get_type(cls):
        for subcls_name, _ in cls.subclasses.items():
            if subcls_name == cls.__name__:
                return subcls_name
        raise NotImplementedError("Must be implemented by subclass")


class MessagePacket(BasePacket):
    """Extension of BasePacket that allows the server and client to send str messages to each other."""

    def __init__(self, data):
        super().__init__(data)

    def verify(self):
        try:
            assert isinstance(self.data, dict)
            assert self.data.get("type") == self.get_type()
            assert self.data.get("content")
            return True
        except AssertionError:
            return False


class KickPacket(BasePacket):
    """Extension of BasePacket that allows the server to kick a user."""

    def __init__(self, data):
        super().__init__(data)

    def verify(self):
        try:
            assert isinstance(self.data, dict)
            assert self.data.get("type") == self.get_type()
            assert self.data.get("reason")
            return True
        except AssertionError:
            return False


if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(
        show_header=True,
        header_style="bold magenta",
        title="Packet Types",
        title_style="bold magenta",
        show_lines=True,
    )

    table.add_column("Name")
    table.add_column("Description")

    for name, cls in BasePacket.subclasses.items():
        table.add_row(name, cls.__doc__)

    console.print(table)
