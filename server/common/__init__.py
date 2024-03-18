from .packets import *
from .registry import BaseRegistry
from .events import EventHandler


class Lock:
    def __init__(self):
        self.locked = False

    def acquire(self):
        while self.locked:
            pass
        self.locked = True

    def release(self):
        self.locked = False
