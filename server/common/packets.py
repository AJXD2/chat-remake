import json
from typing import Union


class VerificationError(Exception):
    pass


class BasePacket(object):
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
    def __init__(self, data):
        super().__init__(data)

    def prep_content(self):
        pass

    def verify(self):
        try:
            assert isinstance(self.data, dict)
            assert self.data.get("type") == self.get_type()
            assert self.data.get("content")
            return True
        except AssertionError:
            return False


class KickPacket(BasePacket):
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
    import os

    termsize = os.get_terminal_size()
    print(
        "=" * round((termsize.columns / 4) - (len(MessagePacket.get_type()) / 2))
        + MessagePacket.get_type()
        + "=" * round((termsize.columns / 4) - (len(MessagePacket.get_type()) / 2))
    )

    msg = MessagePacket({"content": "Hello World!"})
    print(f"Prepped: {msg.prep()}")
    print(f"Decoded: {MessagePacket.decode(msg.prep())}")
    print(
        "=" * round((termsize.columns / 4) - (len(MessagePacket.get_type()) / 2))
        + MessagePacket.get_type()
        + "=" * round((termsize.columns / 4) - (len(MessagePacket.get_type()) / 2))
    )
