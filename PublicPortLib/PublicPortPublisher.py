from twisted.internet import reactor

from PublicPortLib.PublicPortProtocol import PublicPortProtocol


class PublicPortPublisher:
    def __init__(self):
        self.subscribers = []

    def Setup(self):
        reactor.listenMulticast(
            8005,
            PublicPortProtocol("228.0.0.5", 8005, self),
            listenMultiple=True
        )

    def AddSubscriber(self, subscriber):
        self.subscribers.append(subscriber)

    def RemoveSubscriber(self, subscriber):
        self.subscribers.remove(subscriber)

    def SendMessage(self, message):
        for sub in self.subscribers:
            sub.SendMessage(message)
