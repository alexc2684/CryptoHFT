from SMATrader import AutoTrader
from Strategy.SMA_Strategy import SMA

strategy = SMA(1, 2)
a = AutoTrader(strategy, 1, 2)
