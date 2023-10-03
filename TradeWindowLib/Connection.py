import pickle

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol


class TradeData:
    def __init__(self, level, vol, timestamp):
        self.level = level
        self.vol = vol
        self.timestamp = timestamp


class PublicPortClient(DatagramProtocol):
    def __init__(self, gui):
        self.subscribers = []

        self.AddSubscriber(gui)

    def AddSubscriber(self, subscriber):
        self.subscribers.append(subscriber)

    def RemoveSubscriber(self, subscriber):
        self.subscribers.remove(subscriber)

    def startProtocol(self):
        self.transport.joinGroup("228.0.0.5")

    def datagramReceived(self, datagram, addr):
        d = pickle.loads(datagram)

        trade_data = TradeData(d["Level"], d["Volume"], d["Timestamp"])

        for sub in self.subscribers:
            sub.Update(trade_data)
