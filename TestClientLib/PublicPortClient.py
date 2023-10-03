import pickle

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol


class PublicPortClient(DatagramProtocol):
    def startProtocol(self):
        self.transport.joinGroup("228.0.0.5")

    def datagramReceived(self, datagram, addr):
        d = pickle.loads(datagram)

        print(d)


reactor.listenMulticast(8005, PublicPortClient(), listenMultiple=True)
reactor.run()
