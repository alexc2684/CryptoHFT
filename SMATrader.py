import json
import numpy as np
from collections import deque
import asyncio
import websockets
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
        self.i = 0

        start_server = websockets.serve(self.get_websocket_data, "localhost", 8765)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def get_websocket_data(self, websocket, path):
        async for message in websocket:
            await websocket.send(message)
            data = list(map(float, message.split(' ')))
            self.bid_queue.append(data[0])
            self.ask_queue.append(data[1])
            print(self.i)
            self.i += 1
            if len(self.bid_queue) > 2000:
                self.bid_queue.popleft()
                action = self.make_trade(data[0])

    def start_auto_trade(self):
        # while true
        # wait for socket
        # push data to queue
        # each time push executes, hit make_trade
        # ***must be synchronous, unless we lock queue
        pass

    def make_trade(self, curr_price):
        action = self.strategy.choose_action(self.bid_queue, curr_price)
        if self.ORDER_TYPES[action] == "BUY":
            print("BUY")
            #self.client.place_buy_order(self.symbol, self.quantity, curr_price)
        elif self.ORDER_TYPES[action] == "SELL":
            print("SELL")
            #self.client.place_sell_order(self.symbol, self.quantity, curr_price)
        else: #Action == HOLD
            print("HOLD")
            pass
