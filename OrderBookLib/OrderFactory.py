from datetime import datetime

from OrderBookLib.Order import BuyOrder, AskOrder


class OrderFactory:
    orderId = 0

    @classmethod
    def CreateBuyOrder(cls, request):
        cls.orderId += 1

        orderId = OrderFactory.orderId

        return BuyOrder(orderId, float(request["Level"]), int(request["Volume"]),
                             datetime.now().timestamp(), request["OrderType"], request["SessionId"])

    @classmethod
    def CreateAskOrder(cls, request):
        cls.orderId += 1

        orderId = OrderFactory.orderId

        return AskOrder(orderId, float(request["Level"]), int(request["Volume"]),
                        datetime.now().timestamp(), request["OrderType"], request["SessionId"])
