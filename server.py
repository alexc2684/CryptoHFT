from AutoTrader import AutoTrader
from Strategy.SMA_Strategy import SMA

strategy = SMA(1, 10, 100)
a = AutoTrader(strategy, .001, "BTC", "history.csv",  1200)
a.start_auto_trade()
