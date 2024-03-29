import numpy as np
from Strategy import Strategy

class SMA:

    def __init__(self, granularity, price_range, stop_limit):
        self.granularity = granularity
        self.price_range = price_range
        self.stop_limit = stop_limit
        self.state = 1 # 1: buy, 0: sell
        self.buy_price = 0

    def choose_action(self, bid_queue, ask_queue):
        bid_price = bid_queue[len(bid_queue)-1]
        ask_price = ask_queue[len(ask_queue)-1]
        if self.state:
            print("BUY AVG: {} PRICE: {}".format(avg, bid_price))
            avg = sum(bid_queue)/len(bid_queue)
            if avg - self.price_range > bid_price:
                self.state = not self.state
                self.buy_price = round(bid_price + 1, 2)
                return [1, self.buy_price]
        elif not self.state:
            print("PRICE TO SELL AT: {} PRICE: {}".format(self.buy_price + self.price_range, ask_price))
            if ask_price > self.buy_price + self.price_range or ask_price < self.buy_price - self.stop_limit:
                self.state = not self.state
                return [0, round(ask_price - 1, 2)]
        return [2, 0]

