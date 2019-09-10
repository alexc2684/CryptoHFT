import numpy as np
from Strategy import Strategy

class SMA:
    BID_FACTOR = .0001

    def __init__(self, granularity, price_range, stop_limit):
        self.granularity = granularity
        self.price_range = price_range
        self.stop_limit = stop_limit
        self.state = 1 # 1: buy, 0: sell
        self.buy_price = 0

    def choose_action(self, bid_queue, ask_queue):
        curr_price = bid_queue[len(bid_queue)-1]

        if self.state:
            avg = sum(bid_queue)/len(bid_queue)
            if avg - self.price_range > curr_price:
                self.state = not self.state
                return [1, curr_price]
        elif not self.state:
            if curr_price > self.buy_price + self.price_range or curr_price < self.buy_price - self.stop_limit:
                return [0, curr_price]
        return [2, 0]

