import json
import numpy as np
import asyncio
import websockets
from collections import deque
from RobinhoodClient.RobinhoodClient import RobinhoodClient

class AutoTrader:

    ORDER_TYPES = {0: "SELL", 1: "BUY", 2: "HOLD"}

    def __init__(self, strategy, quantity, symbol, max_queue_size = 2000):
        self.bid_queue = deque()
        self.ask_queue = deque()
        self.strategy = strategy
        self.client = RobinhoodClient()
        self.quantity = quantity
        self.symbol = symbol

    def start_auto_trade(self):
        start_server = websockets.serve(self.get_pricing_data, "localhost", 8765)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def get_pricing_data(self, websocket, path):
        async for message in websocket:
            await websocket.send(message)
            data = list(map(float, message.split(' ')))
            #print("BID {} ASK {}".format(data[1], data[0]))
            self.process_data(data[1], data[0])

    def process_data(self, bid_price, ask_price):
        self.bid_queue.append(bid_price)
        self.ask_queue.append(ask_price)
        if len(self.bid_queue) > 2000:
            self.bid_queue.popleft()
            self.ask_queue.popleft()
            action = self.make_trade(self.bid_queue, self.ask_queue)

    def make_trade(self, bid_queue, ask_queue):
        data = self.strategy.choose_action(bid_queue, ask_queue)
        action = data[0]
        price = data[1]
        if self.ORDER_TYPES[action] == "BUY":
            print("BUYING {} {} AT ${}".format(self.symbol, self.quantity, price))
            print("\n")
            self.client.place_buy_order(self.symbol, self.quantity, price)
        elif self.ORDER_TYPES[action] == "SELL":
            print("SELLING {} {} AT ${}".format(self.quantity, self.symbol, price))
            print("\n")
            self.client.place_sell_order(self.symbol, self.quantity, price)
        else: #Action == HOLD
            print("HOLD")
            pass
