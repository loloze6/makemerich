from datetime import datetime, timedelta

import backtrader as bt
from backtrader import Order
from termcolor import colored

class TestStrategy(bt.Strategy):
    params = (
        ('stopafter', 2),
        ('logging', True)
    )
    
    def __init__(self):

        self.bought = False
        # To keep track of pending orders and buy price/commission
        self.order = None
        
    def _log(self, txt):
        if self.p.logging:
            try:
                print(f"{self.datas[0].datetime.datetime(0)}: {txt}")
            except:
                print(f"{datetime.now()}: {txt}")

    def _log_start(self):
        self._log(colored('Starting Portfolio Value: %.2f' % self.broker.getvalue(), 'green'))

    def next(self):

        if self.live_data:
            # Buy
            # size x price should be >10 USDT at a minimum at Binance
            # make sure you use a price that is below the market price if you don't want to actually buy
            # self.order = self.buy(size=2.0, exectype=Order.Limit, price=5.4326)
            self.order = self.buy(size=1)
            # And immediately cancel the buy order
            # self.cancel(self.order)
            self.bought = True
            if self.counttostop:  # stop after x live lines
                self.counttostop -= 1
                if not self.counttostop:
                    self.env.runstop()
                    return
        for data in self.datas:
            self._log('test')
            print('{} - {} | O: {} H: {} L: {} C: {} V:{}'.format(data.datetime.datetime(),
                                                                  data._name, data.open[0], data.high[0], data.low[0],
                                                                  data.close[0], data.volume[0]))
            



    def notify_data(self, data, status, *args, **kwargs):
        if status == data.LIVE:
            self._log('Data live notification')
            self.active = True
        if status == data.DELAYED:
            self._log('Data delayed notification')
            self.active = False

        dn = data._name
        dt = datetime.now()
        msg = 'Data Status: {}, Order Status: {}'.format(data._getstatusname(status), status)
        print(dt, dn, msg)
        if data._getstatusname(status) == 'LIVE':
            self.live_data = True
            self.counttostop = self.p.stopafter
            self.datastatus = 1
        else:
            self.live_data = False
            
            
    #Initialization steps of strategy   
    def start(self):
        self._log_start()
        
        



