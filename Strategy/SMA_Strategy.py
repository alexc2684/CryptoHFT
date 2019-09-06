from Strategy import Strategy

class SMA(Strategy):
    def __init__(self, granularity):
        super(SMA, self).__init__(granularity)

    def choose_action(self, data):
        pass
