from Strategy.SMA_Strategy import SMA
from AutoTrader import AutoTrader

s = SMA(1,10, 5)
a = AutoTrader(s, .0001, 'BTC')

#input data to queue
a.process_data(1,2)

