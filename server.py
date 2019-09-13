from AutoTrader import AutoTrader
from Strategy.MeanReversion import MeanReversion

strategy = MeanReversion(1, 10, 100, 60)
a = AutoTrader(strategy, .001, "BTC", "history.csv",  180)
a.start_auto_trade()
