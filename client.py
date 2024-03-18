from twisted.internet import protocol, reactor

from common.packets import MessagePacket


class ChatClient(protocol.Protocol):
    def __init__(self) -> None:
        reactor.callInThread(self.write_msg)

    def dataReceived(self, data):
        packet = MessagePacket.decode(data)

        if packet:
            print(f"Received: {packet.data['content']}")

    def connectionMade(self):
        msg = MessagePacket({"content": "Hello World!"})
        self.transport.write(msg.prep())

    def send(self, msg):
        msg = MessagePacket({"content": msg})
        self.transport.write(msg.prep())

    def write_msg(self):
        while True:
            self.send(input(""))


class ChatClientFactory(protocol.ClientFactory):
    protocol = ChatClient


if __name__ == "__main__":
    reactor.connectTCP("localhost", 2000, ChatClientFactory())
    reactor.run()
