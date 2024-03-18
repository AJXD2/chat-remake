from threading import Thread
import tkinter as tk
from twisted.internet import protocol, reactor
from twisted.internet.protocol import connectionDone
from twisted.python.failure import Failure
from common.packets import BasePacket, MessagePacket


class ChatClient(protocol.Protocol):
    def __init__(self, app) -> None:
        self.app = app
        reactor.callInThread(self.write_msg)

    def dataReceived(self, data):
        packet = BasePacket.decode(data)
        if packet is None:
            return
        if packet.type == "MessagePacket":
            self.app.display_message(packet.data["content"])
        if packet.type == "KickPacket":
            self.app.display_message(packet.data["reason"])
            self.transport.loseConnection()

    def connectionMade(self):
        self.app.display_message("||| Connected |||")

    def connectionLost(self, reason: Failure = ...) -> None:
        self.app.display_message("||| Disconnected |||")

    def send(self, msg):
        msg = MessagePacket({"content": msg})
        self.transport.write(msg.prep())

    def write_msg(self):
        while True:
            self.send(input(""))


class ChatClientFactory(protocol.ClientFactory):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self.client_protocol = None  # Initialize client_protocol attribute

    protocol = ChatClient

    def buildProtocol(self, addr) -> ChatClient | None:
        self.client_protocol = ChatClient(self.app)  # Store the ChatClient instance
        return self.client_protocol


class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chat Client")
        self.geometry("400x700")

        self.message_frame = tk.Frame(self)
        self.message_frame.pack(fill=tk.BOTH, expand=True)

        self.message_text = tk.Text(self.message_frame, wrap=tk.WORD)
        self.message_text.pack(fill=tk.BOTH, expand=True)
        self.message_text.config(state=tk.DISABLED)
        self.input_frame = tk.Frame(self)
        self.input_frame.pack(fill=tk.X)

        self.input_entry = tk.Entry(self.input_frame)
        self.input_entry.focus_set()
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind(
            "<Return>", self.send_message_on_enter
        )  # Bind Enter key press

        self.send_button = tk.Button(
            self.input_frame, text="Send", command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT)

        self.client = reactor.connectTCP("localhost", 2000, ChatClientFactory(self))

    def send_message(self, event=None):  # Accept event argument for button click
        message = self.input_entry.get()
        if (
            message and self.client.factory.client_protocol
        ):  # Check if client_protocol is set
            self.client.factory.client_protocol.send(message)
            self.input_entry.delete(0, tk.END)

    def send_message_on_enter(
        self, event
    ):  # Function to send message on Enter key press
        self.send_message()

    def display_message(self, message):
        self.message_text.config(state=tk.NORMAL)
        self.message_text.insert(tk.END, message + "\n")
        self.message_text.config(state=tk.DISABLED)


def start_reactor():
    reactor.run(installSignalHandlers=0)


if __name__ == "__main__":
    reactor_thread = Thread(target=start_reactor, daemon=True)
    reactor_thread.start()
    app = ChatApp()

    app.mainloop()
