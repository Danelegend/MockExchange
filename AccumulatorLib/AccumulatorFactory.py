from twisted.internet.protocol import Factory

from AccumulatorLib.AccumulatorProtocol import AccumulatorProtocol


class AccumulatorFactory(Factory):
    def __init__(self, logger, mh, ch):
        self.logger = logger
        self.messageHandler = mh
        self.connectionHandler = ch

    def buildProtocol(self, addr):
        return AccumulatorProtocol(self.connectionHandler)
