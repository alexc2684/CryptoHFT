import json
import asyncio
import websockets
from collections import deque
from RobinhoodClient.RobinhoodClient import RobinhoodClient

class AutoTrader:

    ORDER_TYPES = {0: "SELL", 1: "BUY", 2: "HOLD"}

    def __init__(self, strategy, quantity, symbol, history_filename, max_queue_size = 2000):
        self.bid_queue = deque()
        self.ask_queue = deque()
        self.strategy = strategy
        self.client = RobinhoodClient()
        self.quantity = quantity
        self.symbol = symbol
        self.history_filename = history_filename
        self.max_queue_size = max_queue_size
        self.load_lights()

    def load_lights(self):
        data = open("lights.secret", "r").read()
        data = json.loads(data)
        self.LIGHT1_IP = data['LIGHT1_IP']
        self.PHILLIPS_USER = data['PHILIPS_USER']
        
    def start_auto_trade(self):
        start_server = websockets.serve(self.get_pricing_data, "localhost", 8765)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def get_pricing_data(self, websocket, path):
        async for message in websocket:
            await websocket.send(message)
            data = message.split(' ')
            prices = list(map(float, data[:4]))
            refresh = data[4]
            self.process_data(prices[1], prices[0], prices[2], prices[3], refresh)

    def process_data(self, bid_price, ask_price, mark_price, time, refresh):
        self.bid_queue.append(bid_price)
        self.ask_queue.append(ask_price)
        print("BID {} SELL {}".format(bid_price, ask_price))

        if refresh == "True":
            self.client.refresh_login(False)

        if len(self.bid_queue) > self.max_queue_size:
            self.bid_queue.popleft()
            self.ask_queue.popleft()
            self.make_trade(self.bid_queue, self.ask_queue, mark_price, time)
        elif len(self.bid_queue) % 20 == 0:
            print((self.max_queue_size - len(self.bid_queue))/self.max_queue_size) 
        if len(self.bid_queue) == self.max_queue_size - 1:
            print("TRADER IS ACTIVE")
            
    def write_history(self, bid_price, ask_price, mark_price, action):
        with open(self.history_filename, 'w') as f:
            f.write("{},{},{},{}\n".format(str(bid_price), str(ask_price), str(mark_price), action))

    def make_trade(self, bid_queue, ask_queue, mark_price, time):
        data = self.strategy.choose_action(bid_queue, ask_queue)
        action = data[0]
        price = data[1]
        if self.ORDER_TYPES[action] == "BUY":
            print("BUYING {} {} AT ${}".format(self.symbol, str(self.quantity), str(price)))
            print("\n")
            self.client.place_buy_order(self.symbol, self.quantity, price)
        elif self.ORDER_TYPES[action] == "SELL":
            print("SELLING {} {} AT ${}".format(self.quantity, str(self.symbol), str(price)))
            print("\n")
            self.client.place_sell_order(self.symbol, self.quantity, price)
        else: #Action == HOLD
            print("HOLD at {} at time {}".format(str(mark_price), time))
            pass
        
        self.write_history(bid_queue[len(bid_queue)-1], ask_queue[len(ask_queue)-1], mark_price, self.ORDER_TYPES[action])
