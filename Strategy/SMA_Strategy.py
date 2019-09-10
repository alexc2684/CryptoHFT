from Strategy import Strategy

class SMA:
    BID_FACTOR = .0001

    def __init__(self, granularity, price_range):
        self.granularity = granularity
        self.price_range = price_range
        self.state = 1 # 1: buy, 0: sell

    def choose_action(self, data, curr_price):
        avg = sum(data)/len(data)
        if self.state and avg - avg*self.BID_FACTOR - self.price_range > curr_price:
            self.state = not self.state
            return 1
        elif not self.state and avg + avg*self.BID_FACTOR + self.price_range < curr_price:
            self.state = not self.state
            return 0
        else:
            return 2

