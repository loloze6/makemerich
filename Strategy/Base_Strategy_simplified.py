from datetime import datetime, timedelta

import backtrader as bt
from backtrader import Order
from termcolor import colored

class TestStrategy(bt.Strategy):
    params = (
        ('stopafter', 100),
        ('logging', True)
    )
    
    def __init__(self):

        self.bought = False
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.active = True
        self.counttostop=self.params.stopafter
        
    def _log(self, txt):
        if self.p.logging:
            try:
                print(f"{self.datas[0].datetime.datetime(0)}: {txt}")
            except:
                print(f"{datetime.now()}: {txt}")

    def _log_start(self):
        self._log(colored('Starting Portfolio Value: %.2f' % self.broker.getvalue(), 'green'))
    
    def _log_order(self, order):
        if order.status in [order.Expired]:
            self._log('EXPIRED')
        else:
            self._log('Order ref: {} / Type {} / Status {} / ExecType {} / Size {} / Alive {} / Price {} / Value {} / Comm {}'.format(
                order.ref,
                colored('BUY' if order.isbuy() else 'SELL', 'green' if order.isbuy() else 'red'),
                order.getstatusname(),
                order.exectype,
                order.size,
                order.alive(),
                order.created.price if order.status in [order.Submitted, order.Accepted] else order.executed.price,
                order.created.value if order.status in [order.Submitted, order.Accepted] else order.executed.value,
                order.created.comm if order.status in [order.Submitted, order.Accepted] else order.executed.comm
            ))
       
    def notify_order(self, order):
        self._log_order(order)
    
    def next(self):
            
        if not self.active:
            return
        if not self.position:
            # Buy
            # size x price should be >10 USDT at a minimum at Binance
            # make sure you use a price that is below the market price if you don't want to actually buy
            # self.order = self.buy(size=2.0, exectype=Order.Limit, price=5.4326)
            
            ACTUAL_PRICE = self.datas[0].close[0]
            stop_price = ACTUAL_PRICE*0.9995
            take_profit_price = ACTUAL_PRICE*1.0005
            self._log('Order bracket Price: {} / Stop Price {} / Take Profit Price  {}'.format(
                        ACTUAL_PRICE,
                        stop_price,
                        take_profit_price
                        ))
            #StopPrice is a stop loss limit
            SLparams={'stopPrice': stop_price}
            self.order = self.buy_bracket(price=ACTUAL_PRICE, stopprice=stop_price, limitprice=take_profit_price, stopargs=SLparams)
            
            # self.order = self.buy(size=0.01)
            # And immediately cancel the buy order
            # self.cancel(self.order)
        if self.counttostop:  # stop after x live lines
            self.counttostop -= 1
        if not self.counttostop:
            self.env.runstop()
            return
        for data in self.datas:
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
        
        



