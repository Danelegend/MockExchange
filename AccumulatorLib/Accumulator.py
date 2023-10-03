"""
AccumulatorLib design

An open port that servers can connect to to feed trade requests

Incoming Requests:
 - Insert Order (EOD, FAK, FOR)
 - Cancel Order
 - Cancel All Orders
 - Correction Order (Change the volume of an alrdy inputted order --> Can only decrease, any extra is added to end of lvl)

 - Validation (used to authenticate a user)

Outgoing Responses:
 - Insert Order Confirmation (with order id)
 - Order Cancellation
 - Cancel All Orders Confirmation

 - Validation Confirmation

 We can use the reactor model (twisted) to listen for requests in a single-threaded manner
"""
from twisted.logger import Logger, jsonFileLogObserver
from twisted.internet import reactor, task

from AccumulatorLib.AccumulatorFactory import AccumulatorFactory
from AccumulatorLib.MessageHandler import MessageHandler
from AccumulatorLib.ConnectionHandler import ConnectionHandler

from PublicPortLib.PublicPortPublisher import PublicPortPublisher

from OrderBookLib.OrderBook import OrderBook


def SetupCallback(fn, time, *args):
    callback = task.LoopingCall(fn, *args)
    callback.start(time)


if __name__ == '__main__':
    logger = Logger(observer=jsonFileLogObserver(open("log.json", "w")))

    pp = PublicPortPublisher()

    ob = OrderBook(logger, pp)

    mh = MessageHandler(logger, ob)
    ch = ConnectionHandler(logger, mh)

    SetupCallback(ConnectionHandler.PruneUnidentifiedConnectionsCallback, 5, ch)

    pp.Setup()

    reactor.listenTCP(8080, AccumulatorFactory(logger, mh, ch))
    reactor.run()
