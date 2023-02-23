import backtrader as bt
from backtrader.indicators import ExponentialMovingAverage as EMA
from termcolor import colored

class EMA_strategy(bt.Strategy):
    params = (   
        ('ema_period', 10),
    )

    def __init__(self):
    #EMA
        self.ema = EMA(period=self.p.ema_period)
        self.candle_open = 0
    def log(self, msg, dt=None):
        print("{} - {}".format(dt or self.datas[0].datetime.date(0), msg))
    def next(self):
        #self.log('{} - {} {} @ {}'.format(self.datas[0].datetime.date(0), self.datas[0].close[0], self.datas[0]._name, self.ema[0]))
    #EMA
        #self.log('Close: {}, EMA: {}'.format(self.datas[0].close[0], self.ema[0]))
        self.log('Close: {}, IsDoji: {}'.format(self.datas[0].close[0], self.doji.is_doji[0]))
        if not self.position:
        #EMA
            if self.datas[0].close[0] < self.ema[0]:
                orders = [self.buy()]
            #Example of trades type
                #orders = [self.buy(), self.sell(exectype=bt.Order.Stop, price=self.data.close[0] * 0.99)]
            # or
                #orders = [self.buy(), self.sell(exectype=bt.Order.Limit, price=self.data.close[0] * 1.01)]
                self.orders_ref = [order.ref for order in orders if order]
        if self.datas[0].close[0] > self.ema[0]:
            self.close()
    #Exemple of data print
        #print(self.datas[0].volume[0])
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

            # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(colored('BUY EXECUTED, %.2f' % order.executed.price, 'blue'))
            elif order.issell():
                self.log(colored('SELL EXECUTED, %.2f' % order.executed.price, 'yellow'))

            # Not enough cash: order rejected
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
            # We remove order if it's useless    
        if not order.alive() and order.ref in self.orders_ref:
            self.orders_ref.remove(order.ref)

    def notify_trade(self, trade):
        #self.log('{} - {} {} @ {}'.format(trade.dtopen, trade.size, trade.data._name, trade.price))
        if trade.isclosed:
            self.log(colored('PROFIT, %.2f' % (trade.pnl), 'green') if trade.pnl > 0
                    else colored('LOSS, %.2f' % (trade.pnl), 'red'))