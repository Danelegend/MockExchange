import pickle

from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

from AccumulatorLib.MessageHandler import RequestIds, ResponseIds
from OrderBookLib.Order import OrderType

class Client(Protocol):
    def __init__(self):
        self.session_id = -1

    def sendMessage(self, request):
        print("Sending Msg - " + str(request))
        self.transport.write(request)
        print("Msg sent - " + str(request))


    def dataReceived(self, data: bytes):
        try:
            d = pickle.loads(data)

            self.handleParse(d)
        except Exception as e:
            print(e)

    def connectionLost(self, reason):
        print("Disconnected")

    def handleParse(self, d):
        if d["MessageId"] == ResponseIds.CONNECTION_ESTABLISHED.value:
            self.session_id = d["SessionId"]
        else:
            print(d)

    def sendLogin(self):
        d = {
            "MessageId": RequestIds.LOGIN_REQUEST.value,
            "SessionId": self.session_id,
            "LoginKey": "ABC",
            "LoginPassword": "123",
        }

        try:
            l = pickle.dumps(d)
        except Exception as e:
            print("Exception")

        self.sendMessage(l)

    def sendOrder(self, direction, volume, level):
        d = {
            "MessageId": RequestIds.ORDER_REQUEST.value,
            "SessionId": self.session_id,
            "OrderType": OrderType.END_OF_DAY.value,
            "Direction": direction,
            "Volume": volume,
            "Level": level,
        }

        l = pickle.dumps(d)

        self.sendMessage(l)

    def getOrderBook(self):
        d = {
            "MessageId": 0x0010,
            "SessionId": self.session_id,
        }

        self.sendMessage(pickle.dumps(d))


def useProtocol(p):
    #p.sendMessage("I have connected")
    reactor.callLater(1, p.sendLogin)
    reactor.callLater(2, p.sendOrder, 0, 100, 5)
    reactor.callLater(3, p.getOrderBook)
    reactor.callLater(4, p.sendOrder, 1, 100, 5)
    reactor.callLater(5, p.getOrderBook)


if __name__ == '__main__':
    point = TCP4ClientEndpoint(reactor, "localhost", 8080)
    d = connectProtocol(point, Client())
    d.addCallback(useProtocol)
    reactor.run()
