from datetime import datetime, timedelta

import backtrader as bt
from backtrader import Order


class TestStrategy(bt.Strategy):

    def __init__(self):

        self.bought = False
        # To keep track of pending orders and buy price/commission
        self.order = None

    def next(self):

        if self.live_data and not self.bought:
            # Buy
            # size x price should be >10 USDT at a minimum at Binance
            # make sure you use a price that is below the market price if you don't want to actually buy
            # self.order = self.buy(size=2.0, exectype=Order.Limit, price=5.4326)
            self.order = self.buy()
            # And immediately cancel the buy order
            self.cancel(self.order)
            self.bought = True

        for data in self.datas:
            print('{} - {} | O: {} H: {} L: {} C: {} V:{}'.format(data.datetime.datetime(),
                                                                  data._name, data.open[0], data.high[0], data.low[0],
                                                                  data.close[0], data.volume[0]))

    def notify_data(self, data, status, *args, **kwargs):
        dn = data._name
        dt = datetime.now()
        msg = 'Data Status: {}, Order Status: {}'.format(data._getstatusname(status), status)
        print(dt, dn, msg)
        if data._getstatusname(status) == 'LIVE':
            self.live_data = True
        else:
            self.live_data = False
