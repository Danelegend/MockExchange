from OrderBookLib.BookHandler import BuyBookHandler, AskBookHandler, BuyOrder, AskOrder
from OrderBookLib.Order import OrderType


class OrderBook:
    """
    The order book is a data structure
    It:
     - Holds all active orders
     - Knows the top bid and top ask order
    """

    def __init__(self, logger, publicPublisher):
        self.logger = logger

        self.buy_book = BuyBookHandler(logger, publicPublisher)
        self.ask_book = AskBookHandler(logger, publicPublisher)

    def LogMessage(self, message):
        self.logger.info("[OrderBook]: " + message)

    def ReceiveBidOrder(self, order: BuyOrder):
        d = {
            "OrderId": order.id,
            "Filled": False,
            "VolumeFilled": 0,
            "VolumeRemaining": order.volume,
            "LevelsFilled": {},
        }

        if order.orderType == OrderType.END_OF_DAY.value:
            remaining_order, levels_filled = self.ask_book.RunOrder(order)

            self.LogMessage("Placing excess bid order from %d to %d at level %d, orderId=%d"
                            % (order.volume, remaining_order.volume, order.level, order.id))

            self.buy_book.InsertOrder(remaining_order)

            d["Filled"] = remaining_order.volume == 0
            d["VolumeRemaining"] = remaining_order.volume
            d["LevelsFilled"] = levels_filled

        elif order.orderType == OrderType.FILL_AND_KILL.value:
            remaining_order, levels_filled = self.ask_book.RunOrder(order)

            d["Filled"] = remaining_order.volume == 0
            d["VolumeRemaining"] = remaining_order.volume
            d["LevelsFilled"] = levels_filled

        return d

    def ReceiveAskOrder(self, order: AskOrder):
        d = {
            "OrderId": order.id,
            "Filled": False,
            "VolumeFilled": 0,
            "VolumeRemaining": order.volume,
            "LevelsFilled": {},
        }

        if order.orderType == OrderType.END_OF_DAY.value:
            remaining_order, levels_filled = self.buy_book.RunOrder(order)

            self.LogMessage("Placing excess ask order from %d to %d at level %d, orderId=%d"
                            % (order.volume, remaining_order.volume, order.level, order.id))

            self.ask_book.InsertOrder(remaining_order)

            d["Filled"] = remaining_order.volume == 0
            d["VolumeRemaining"] = remaining_order.volume
            d["LevelsFilled"] = levels_filled

        elif order.orderType == OrderType.FILL_AND_KILL.value:
            remaining_order, levels_filled = self.buy_book.RunOrder(order)

            d["Filled"] = remaining_order.volume == 0
            d["VolumeRemaining"] = remaining_order.volume
            d["LevelsFilled"] = levels_filled

        return d

    def print(self):
        print("Bids: " + str(self.buy_book.volumes))
        print("Asks: " + str(self.ask_book.volumes))
