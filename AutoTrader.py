import json
import numpy as np
import asyncio
import websockets
from RobinhoodClient.RobinhoodClient import RobinhoodClient

class AutoTrader:

    ORDER_TYPES = {0: "SELL", 1: "BUY", 2: "HOLD"}

    def __init__(self, strategy, quantity, symbol, max_queue_size = 2000):
        self.data_queue = np.empty([2000, 3])
        self.strategy = strategy
        self.client = RobinhoodClient()
        self.quantity = quantity
        self.symbol = symbol

        start_server = websockets.serve(self.get_pricing_data, "localhost", 8765)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def get_pricing_data(self, websocket, path):
        async for message in websocket:
            await websocket.send(message)
            data = list(map(float, message.split(' ')))
            process_data(data)

    def process_data(self, data):
        self.data_queue = np.append(self.data_queue, data)
        if self.data_queue.shape[0] > 2000:
            self.data_queue = self.data_queue[1:]
            action = self.make_trade(self.data_queue)
        print(self.data_queue)

    def make_trade(self, data):
        action, price = self.strategy.choose_action(data)
        if self.ORDER_TYPES[action] == "BUY":
            print("BUYING {} {}".format(self.symbol, self.quantity))
            #self.client.place_buy_order(self.symbol, self.quantity, price)
        elif self.ORDER_TYPES[action] == "SELL":
            print("SELLING {} {}".format(self.quantity, self.symbol))
            #self.client.place_sell_order(self.symbol, self.quantity, price)
        else: #Action == HOLD
            print("HOLD")
            pass
