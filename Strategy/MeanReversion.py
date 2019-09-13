 import numpy as np

 class MeanReversion:

     def __init__(self, granularity, price_range, stop_limit, short_avg_time):
         self.granularity = granularity
         self.price_range = price_range
         self.stop_limit = stop_limit
         self.state = 1 # 1: buy, 0: sell
         self.buy_price = 0
         self.short_avg_time = short_avg_time

     def choose_action(self, bid_queue, ask_queue):
         bid_price = bid_queue[len(bid_queue)-1]
         short_bid = bid_queue[len(bid_queue) - self.short_avg_time:]
         ask_price = ask_queue[len(ask_queue)-1]
         short_ask = ask_queue[len(ask_queue) - self.short_avg_time:]
         if self.state:
             long_avg = sum(bid_queue)/len(bid_queue)
             short_avg = sum(short_bid)/len(short_bid)
             if short_avg < long_avg - self.price_range:
                 print("BUY AVG: {} PRICE: {}".format(avg, bid_price))
                 self.state = not self.state
                 self.buy_price = round(bid_price + 1, 2)
                 return [1, self.buy_price]
         elif not self.state:
             long_avg = sum(ask_queue)/len(ask_queue)
             short_avg = sum(short_ask)/len(short_ask)
             if short_avg > long_avg + self.price_range and short_avg > self.buy_price:
                 print("PRICE TO SELL AT: {} PRICE: {}".format(self.buy_price + self.price_range, ask_price))
                 self.state = not self.state
                 return [0, round(ask_price - 1, 2)]
         return [2, 0]
