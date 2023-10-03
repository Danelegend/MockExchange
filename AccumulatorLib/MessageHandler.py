import pickle
from datetime import datetime
from enum import Enum

from AccumulatorLib.Connection import Connection
from OrderBookLib.Order import Order
from OrderBookLib.OrderFactory import OrderFactory

"""
Messages we sent are of the form 0x1XXX
Messages we receive are of the form 0x0001
"""


class ResponseIds(Enum):
    RESPONSE_MASK = 0x1000

    CONNECTION_ESTABLISHED = 0x1001
    LOGIN_RESPONSE = 0x1002
    ORDER_CONFIRMATION = 0x1006
    ORDER_RESPONSE = 0x1007


class RequestIds(Enum):
    LOGIN_REQUEST = 0x0002
    ORDER_REQUEST = 0x0006


class RequestAttributes(Enum):
    LOGIN_REQUEST = ["MessageId", "SessionId", "LoginKey", "LoginPassword"]
    ORDER_REQUEST = ["MessageId", "SessionId", "OrderType", "Direction", "Volume", "Level"]


class MessageHandler:
    MESSAGE_HANDLER_PREFIX = "[MessageHandler] "

    def __init__(self, logger, orderbook):
        self.logger = logger
        self.orderbook = orderbook

    def LogMessage(self, message):
        self.logger.info(self.MESSAGE_HANDLER_PREFIX + message)

    def LogError(self, message):
        self.logger.error(self.MESSAGE_HANDLER_PREFIX + message)

    def ParseMessage(self, encodedMessage, conn: Connection):
        try:
            d = pickle.loads(encodedMessage)

            if "MessageId" not in d:
                self.LogMessage("Request does not contain MessageId connectionId=%d" % conn.id)
                return
            elif "SessionId" not in d:
                self.LogMessage("Request does not contain SessionId connectionId=%d" % conn.id)
                return
            elif d["SessionId"] != conn.id:
                self.LogMessage("SessionId does not match with connection id, connectionId=%d" % conn.id)
                return
            elif d["MessageId"] & ResponseIds.RESPONSE_MASK.value == ResponseIds.RESPONSE_MASK.value:
                self.LogMessage("Request not recognised as request connectionId=%d" % conn.id)
                return

            self.HandleDecodedMessage(d, conn)

        except pickle.UnpicklingError as e:
            self.LogMessage("Cannot unpickle message sent from connectionId=%d" % conn.id)

    def HasAttributes(self, decodedMessage):
        def check_attributes(d, attributes):
            for attribute in attributes:
                if attribute not in d:
                    return False

            return True

        messageId = decodedMessage["MessageId"]

        if messageId == RequestIds.LOGIN_REQUEST.value:
            return check_attributes(decodedMessage, RequestAttributes.LOGIN_REQUEST.value)
        elif messageId == RequestIds.ORDER_REQUEST.value:
            return check_attributes(decodedMessage, RequestAttributes.ORDER_REQUEST.value)
        elif messageId == 0x0010:
            return True

        return False


    def SendConnectionEstablisedMessage(self, conn: Connection):
        d = {
            "MessageId": ResponseIds.CONNECTION_ESTABLISHED.value,
            "SessionId": conn.id,
            "ConnectionTime": conn.joinTime,
            "CurrentTime": datetime.now().timestamp(),
            }

        conn.SendMessage(pickle.dumps(d))

    def HandleDecodedMessage(self, decodedMessage, conn):
        if not self.HasAttributes(decodedMessage):
            return

        messageId = decodedMessage["MessageId"]

        if messageId == RequestIds.LOGIN_REQUEST.value:
            self.HandleLoginRequest(decodedMessage, conn)
        elif messageId == RequestIds.ORDER_REQUEST.value:
            self.HandleOrderMessage(decodedMessage, conn)
        elif messageId == 0x0010:
            self.orderbook.print()

    def HandleLoginRequest(self, loginRequest, conn):
        """
        Login Request has:
         - MessageId
         - SessionId
         - Login Key
         - Login Password
        """
        if self.LoginCredentialsMatch(loginRequest["LoginKey"], loginRequest["LoginPassword"]):
            conn.loggedIn = True

        self.SendLoginResponse(conn)

    def SendLoginResponse(self, conn: Connection):
        d = {
            "MessageId": ResponseIds.LOGIN_RESPONSE.value,
            "SessionId": conn.id,
            "LoginSuccess": conn.loggedIn,
        }

        conn.SendMessage(pickle.dumps(d))

    def LoginCredentialsMatch(self, key, password):
        return key == "ABC" and password == "123"

    def SendOrderConfirmationResponse(self, conn: Connection, order: Order):
        d = {
            "MessageId": ResponseIds.ORDER_CONFIRMATION.value,
            "SessionId": conn.id,
            "OrderId": order.id,
        }

        conn.SendMessage(pickle.dumps(d))

    def HandleOrderMessage(self, orderRequest, conn):
        """
        Order Request has:
         - MessageId
         - SessionId
         - OrderType (EOD, FAK, FOK)
         - Direction (0 = BID | 1 = ASK)
         - Volume
         - Level
        """
        if orderRequest["Direction"] == 0:
            order = OrderFactory.CreateBuyOrder(orderRequest)

            self.SendOrderConfirmationResponse(conn, order)

            order_receipt = self.orderbook.ReceiveBidOrder(order)

            self.SendOrderReceipt(conn, order_receipt)
        elif orderRequest["Direction"] == 1:
            order = OrderFactory.CreateAskOrder(orderRequest)

            self.SendOrderConfirmationResponse(conn, order)

            order_receipt = self.orderbook.ReceiveAskOrder(order)

            self.SendOrderReceipt(conn, order_receipt)

    def SendOrderReceipt(self, conn: Connection, orderReceipt):
        """
        Order Confirmation:
         - SessionId
         - OrderId
         - Filled
         - Volume Filled
         - Volume Remaining
         - Levels Filled
        """

        d = {
            "MessageId": ResponseIds.ORDER_RESPONSE.value,
            "SessionId": conn.id,
            "OrderId": orderReceipt["OrderId"],
            "Filled": orderReceipt["Filled"],
            "VolumeFilled": orderReceipt["VolumeFilled"],
            "VolumeRemaining": orderReceipt["VolumeRemaining"],
            "LevelsFilled": orderReceipt["LevelsFilled"]
        }

        conn.SendMessage(pickle.dumps(d))
