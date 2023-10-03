from twisted.internet.protocol import DatagramProtocol


class PublicPortProtocol(DatagramProtocol):
    def __init__(self, host, port, pp):
        self.host = host
        self.port = port
        self.pp = pp

        self.pp.AddSubscriber(self)

    def startProtocol(self):
        self.transport.setTTL(5)

        self.transport.joinGroup("228.0.0.5")

    def SendMessage(self, message):
        self.transport.write(message, (self.host, self.port))

    def stopProtocol(self):
        self.pp.RemoveSubscriber(self)
