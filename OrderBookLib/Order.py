from enum import Enum
from datetime import datetime


class OrderType(Enum):
    END_OF_DAY = "EOD"
    FILL_AND_KILL = "FAK"
    FILL_OR_KILL = "FOK"


class Order:
    def __init__(self, id, level, volume, timestamp, orderType, placerId):
        self.id = id
        self.level = level
        self.volume = volume
        self.timestamp = timestamp

        self.orderType = orderType

        self.traderId = placerId

    def CanBeBoughtOut(self, order):
        return order.volume >= self.volume


class BuyOrder(Order):
    def __init__(self, id, level, volume, timestamp, orderType, placerId):
        super().__init__(id, level, volume, timestamp, orderType, placerId)

    def __cmp__(self, other):
        if not isinstance(other, BuyOrder):
            return NotImplemented

        return True if self.level > other.level else self.timestamp <= other.timestamp


class AskOrder(Order):
    def __init__(self, id, level, volume, timestamp, orderType, placerId):
        super().__init__(id, level, volume, timestamp, orderType, placerId)

    def __cmp__(self, other):
        if not isinstance(other, AskOrder):
            return NotImplemented

        return True if self.level < other.level else self.timestamp <= other.timestamp


class OrderReceipt:
    def __init__(self, hitId, quoteId, hitOrderId, level, volume):
        self.hitter_id = hitId
        self.quoter_id = quoteId

        self.hit_order_id = hitOrderId

        self.level = level
        self.volume = volume

        self.tradeComplete = datetime.now().timestamp()
