

class AutoTrader:

    ORDER_TYPES = {0: "SELL", 1:"BUY", 2:"HOLD"}

    def __init__(self, strategy, quantity, symbol):
        self.data_queue = []
        self.strategy = strategy
        self.client = RobinhoodClient()
        self.quantity = quantity
        self.symbol = symbol

    def start_auto_trade(self):
        # init push queue
        # each time push executes, hit make_trade
        pass

    def make_trade(self, curr_price):
        action = self.strategy.choose_action(self.data_queue, curr_price)
        if self.ORDER_TYPES[action] == "BUY":
            self.client.place_buy_order(self.symbol, self.quantity, curr_price)
        elif self.ORDER_TYPES[action] == "SELL":
            self.client.place_sell_order(self.symbol, self.quantity, curr_price)
        else: #Action == HOLD
            pass
