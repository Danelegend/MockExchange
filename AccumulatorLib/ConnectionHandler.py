"""
ConnectionHandler Design

 - Responsible for handling connections
    - That being it determines whether a connection has been logged in or if it is idle
    - It will also kick off idle connections after 10s

TODO: Think of how PubSub could be implemented to decouple
      - Given sessionId, we can get protocols and send responses
"""
from datetime import datetime

from AccumulatorLib.Connection import Connection


class ConnectionHandler:
    def __init__(self, logger, mh):
        self.logger = logger
        self.messageHandler = mh

        self.connectionId = 0
        self.connections = {}
        self.unidentifiedConnections = []

    def AddNewConnection(self, protocol):
        self.connectionId += 1

        protocol.SetConnectionId(self.connectionId)

        conn = Connection(protocol.GetConnectionId(), protocol, datetime.now().timestamp())

        self.connections[conn.id] = conn

        self.unidentifiedConnections.append(conn)
        self.logger.info("New connection with connectionId=%d" % conn.id)

        self.messageHandler.SendConnectionEstablisedMessage(conn)

    def RemoveConnection(self, conn):
        self.logger.info("Kicking connection with connectionId=%d" % conn.id)

        conn.protocol.transport.loseConnection()

    def LoseConnection(self, protocol, reason):
        self.logger.info("Connection has been lost with connectionId=%d" % protocol.GetConnectionId())

        self.HandleDisconnectedSession(protocol.GetConnectionId())

    def HandleDisconnectedSession(self, connId):
        """
        If session was never logged in, remove
        If session was logged in, set disconnected
        """
        if connId not in self.connections:
            return

        conn = self.connections[connId]

        if not conn.loggedIn:
            self.connections.pop(connId)
        else:
            self.connections[connId].loggedIn = False

    def HandleMessage(self, encodedMessage, connId):
        self.messageHandler.ParseMessage(encodedMessage, self.connections[connId])

    def GetConnection(self, connectionId):
        return self.connections[connectionId]

    def PruneUnidentifiedConnections(self):
        """
        Think of unidentifiedConnections as a queue
        Loop through until we find a connection with time <=10s
        Remove all connections
        Those who are not logged in get kicked
        """
        while len(self.unidentifiedConnections) > 0 and GetSecondsRemaining(self.unidentifiedConnections[0]) > 10:
            conn = self.unidentifiedConnections[0]
            self.unidentifiedConnections.pop(0)

            if not conn.loggedIn:
                self.logger.info("Connection with connectionId=%d has not logged in | Pruning" % conn.id)
                self.RemoveConnection(conn)

    @classmethod
    def PruneUnidentifiedConnectionsCallback(cls, ch):
        ch.PruneUnidentifiedConnections()


def GetSecondsRemaining(conn: Connection):
    currTime = datetime.now()

    ts = conn.joinTime
    time = datetime.fromtimestamp(ts)

    return (currTime - time).total_seconds()
