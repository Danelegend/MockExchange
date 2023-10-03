import pickle

from abc import ABC, abstractmethod
from datetime import datetime

from OrderBookLib.PriorityQueue import OrderPriorityQueue
from OrderBookLib.Order import Order, BuyOrder, AskOrder, OrderReceipt


class OrderBookHandler(ABC):
    def __init__(self, logger, pp):
        self.logger = logger
        self.publicPublisher = pp

        self.activeOrders = OrderPriorityQueue()
        self.volumes = {}

    def LogMessage(self, message):
        self.logger.info("[OrderBookHandler]: " + message)

    def GetTopLevel(self):
        return self.activeOrders.peek().level

    def GetTopLevelVolume(self):
        return self.GetLevelVolume(self.GetTopLevel())

    def GetLevelVolume(self, level):
        if level not in self.volumes:
            return 0

        return self.volumes[level]

    def InsertOrder(self, order: Order):
        self.activeOrders.put(order)

        if order.level not in self.volumes:
            self.volumes[order.level] = 0

        self.volumes[order.level] += order.volume

    def PublishTrade(self, level, volume):
        d = {
            "MessageId": 0x1100,
            "Level": level,
            "Volume": volume,
            "Timestamp": datetime.now().timestamp()
        }

        self.publicPublisher.SendMessage(pickle.dumps(d))

    @abstractmethod
    def RunOrder(self, order: Order):
        self.LogMessage("Running order, orderId=%d level=%d volume=%d", order.id, order.level, order.volume)

    @abstractmethod
    def CanRunFullOrder(self):
        pass

    def CompleteOrder(self, order):
        topOrder = self.activeOrders.peek()
        volBought = min(topOrder.volume, order.volume)

        if topOrder.CanBeBoughtOut(order):
            self.activeOrders.get()

            order.volume -= volBought
        else:
            self.activeOrders.peek().volume -= volBought

            order.volume = 0

        self.volumes[topOrder.level] -= volBought

        return order, OrderReceipt(order.traderId, topOrder.traderId, topOrder.id, topOrder.level, volBought)


class BuyBookHandler(OrderBookHandler):
    def __init__(self, logger, pp):
        super().__init__(logger, pp)

    def CanRunFullOrder(self):
        pass

    def RunOrder(self, order: AskOrder):
        """
        We want to go through and hit each of the orders until
        we exceed the level specified in order

        Precondition: Order must be of the opposite type
        """

        # Keep polling orders until we reach a level below what
        # we want
        receipts = []
        levels_filled = {}

        while order.volume > 0 and not self.activeOrders.empty() and self.activeOrders.peek().level >= order.level:
            order, receipt = self.CompleteOrder(order)

            self.LogMessage("Trade occured between quoter=%d and hitter=%d for vol=%d level=%d orderId=%d" %
                            (receipt.quoter_id, receipt.hitter_id, receipt.volume, receipt.level, receipt.hit_order_id))

            receipts.append(receipt)
            self.PublishTrade(receipt.level, receipt.volume)

            if receipt.level not in levels_filled:
                levels_filled[receipt.level] = 0
            levels_filled[receipt.level] += receipt.volume

        return order, levels_filled


class AskBookHandler(OrderBookHandler):
    def __init__(self, logger, pp):
        super().__init__(logger, pp)

    def CanRunFullOrder(self):
        pass

    def RunOrder(self, order: BuyOrder):
        receipts = []
        levels_filled = {}

        while order.volume > 0 and not self.activeOrders.empty() and self.activeOrders.peek().level <= order.level:
            order, receipt = self.CompleteOrder(order)

            self.LogMessage("Trade occured between quoter=%d and hitter=%d for vol=%d level=%d orderId=%d" %
                            (receipt.quoter_id, receipt.hitter_id, receipt.volume, receipt.level, receipt.hit_order_id))

            receipts.append(receipt)
            self.PublishTrade(receipt.level, receipt.volume)

            if receipt.level not in levels_filled:
                levels_filled[receipt.level] = 0
            levels_filled[receipt.level] += receipt.volume

        return order, levels_filled
