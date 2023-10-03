class Connection:
    def __init__(self, id, protocol, joinTime, loggedIn=False, lastMessageTime=-1):
        self.id = id
        self.protocol = protocol
        self.loggedIn = loggedIn
        self.joinTime = joinTime

        self.lastMessageTime = lastMessageTime

    def SendMessage(self, message):
        self.protocol.transport.write(message)
