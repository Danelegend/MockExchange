from twisted.internet.protocol import Protocol


class AccumulatorProtocol(Protocol):
    def __init__(self, ch):
        self.connectionHandler = ch

        self.connectionId = -1

    def connectionMade(self):
        self.connectionHandler.AddNewConnection(self)

    def dataReceived(self, line):
        self.connectionHandler.HandleMessage(line, self.connectionId)

    def connectionLost(self, reason):
        self.connectionHandler.LoseConnection(self, reason)

    def SetConnectionId(self, connId):
        self.connectionId = connId

    def GetConnectionId(self):
        return self.connectionId
