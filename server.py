from AutoTrader import AutoTrader
from Strategy.SMA_Strategy import SMA

strategy = SMA(1, 10, 5)
a = AutoTrader(strategy, .001, "BTC")
a.start_auto_trade()
