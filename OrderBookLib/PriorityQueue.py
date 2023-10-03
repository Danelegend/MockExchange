from queue import PriorityQueue


class OrderPriorityQueue(PriorityQueue):
    def peek(self):
        if self.empty():
            raise IndexError

        return self.queue[0]
