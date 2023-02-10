import backtrader as bt
from backtrader.indicators import ExponentialMovingAverage as EMA
from termcolor import colored

class BracketStrategy(bt.Strategy):

    params = (
        ('ema_period', 10),
        ('stop_loss', 0),
        ('take_profit', 0),
        ('risk_reward_ratio', 0),
    )
    
    def __init__(self):
        self.orders_ref = list()
        self.ema = EMA(period=self.p.ema_period)
    
    def log(self, msg, dt=None):
        print("{} - {}".format(dt or self.datas[0].datetime.date(0), msg))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(colored('BUY EXECUTED, %.2f' % order.executed.price, 'blue'))
                self.buy_price = order.executed.price
            elif order.issell():
                self.log(colored('SELL EXECUTED, %.2f' % order.executed.price, 'yellow'))

        if not order.alive() and order.ref in self.orders_ref:
            self.orders_ref.remove(order.ref)

    def next(self):
        self.log('Close: {}, EMA: {}'.format(self.datas[0].close[0], self.ema[0]))

        if not self.position:
            orders = []

            if self.datas[0].close[0] < self.ema[0]:
                stop_price, take_profit_price = self.get_stop_tp_prices('long')
                orders = self.get_orders('long', stop_price, take_profit_price)
                self.log_orders(stop_price, take_profit_price, 'long')

            if self.datas[0].close[0] > self.ema[0]:
                stop_price, take_profit_price = self.get_stop_tp_prices('short')
                orders = self.get_orders('short', stop_price, take_profit_price)
                self.log_orders(stop_price, take_profit_price, 'short')

            self.orders_ref = [order.ref for order in orders if order]

    def get_stop_tp_prices(self, side):
        if side == 'long':
            stop_price = self.datas[0].close[0]
            if self.p.stop_loss:
                stop_price = self.datas[0].close[0] * (1 - self.p.stop_loss / 100)

            take_profit_price = self.datas[0].close[0]
            if self.p.take_profit:
                take_profit_price = self.datas[0].close[0] * (1 + self.p.take_profit / 100)

            if self.p.risk_reward_ratio:
                take_profit_price = self.datas[0].close[0] + (
                            self.datas[0].close[0] - stop_price) * self.params.risk_reward_ratio

            return stop_price, take_profit_price

        if side == 'short':
            stop_price = self.datas[0].close[0]
            if self.p.stop_loss:
                stop_price = self.datas[0].close[0] * (1 + self.p.stop_loss / 100)

            take_profit_price = self.datas[0].close[0]
            if self.p.take_profit:
                take_profit_price = self.datas[0].close[0] * (1 - self.p.take_profit / 100)

            if self.p.risk_reward_ratio:
                take_profit_price = self.datas[0].close[0] - (
                            stop_price - self.datas[0].close[0]) * self.params.risk_reward_ratio

            return stop_price, take_profit_price

    def get_orders(self, side, stop_price, take_profit_price):

        ACTUAL_PRICE = self.datas[0].close[0]
        orders = list()

        if side == 'long':
            if stop_price != ACTUAL_PRICE and take_profit_price != ACTUAL_PRICE:
                orders = self.buy_bracket(price=ACTUAL_PRICE, stopprice=stop_price, limitprice=take_profit_price)
            elif stop_price != ACTUAL_PRICE and take_profit_price == ACTUAL_PRICE:
                orders = [self.buy(), self.sell(exectype=bt.Order.Stop, price=stop_price)]
            elif stop_price == ACTUAL_PRICE and take_profit_price != ACTUAL_PRICE:
                orders = [self.buy(), self.sell(exectype=bt.Order.Limit, price=take_profit_price)]
            else:
                orders = [self.buy()]

        if side == 'short':
            if stop_price != ACTUAL_PRICE and take_profit_price != ACTUAL_PRICE:
                orders = self.sell_bracket(price=ACTUAL_PRICE, stopprice=stop_price, limitprice=take_profit_price)
            elif stop_price != ACTUAL_PRICE and take_profit_price == ACTUAL_PRICE:
                orders = [self.sell(), self.buy(exectype=bt.Order.Stop, price=stop_price)]
            elif stop_price == ACTUAL_PRICE and take_profit_price != ACTUAL_PRICE:
                orders = [self.sell(), self.buy(exectype=bt.Order.Limit, price=take_profit_price)]
            else:
                orders = [self.sell()]

        return orders

    def log_orders(self, stop_price, take_profit_price, side):
        if side == 'long':
            self.log(colored('BUY CREATE, %.2f' % self.datas[0].close[0], 'blue'))
            if stop_price != self.datas[0].close[0]:
                self.log(colored('STOP CREATE, %.2f' % stop_price, 'red'))
            if take_profit_price != self.datas[0].close[0]:
                self.log(colored('TAKE PROFIT CREATE, %.2f' % take_profit_price, 'green'))

        if side == 'short':
            self.log(colored('SELL CREATE, %.2f' % self.datas[0].close[0], 'yellow'))
            if stop_price != self.datas[0].close[0]:
                self.log(colored('STOP CREATE, %.2f' % stop_price, 'red'))
            if take_profit_price != self.datas[0].close[0]:
                self.log(colored('TAKE PROFIT CREATE, %.2f' % take_profit_price, 'green'))
