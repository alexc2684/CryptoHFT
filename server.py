from AutoTrader import AutoTrader
from Strategy.SMA_Strategy import SMA

strategy = SMA(1, 10, 50)
a = AutoTrader(strategy, .001, "BTC", "history.csv",  300)
a.start_auto_trade()
