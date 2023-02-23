import backtrader as bt
from abc import abstractmethod
from termcolor import colored
from datetime import datetime
class BaseStrategy(bt.Strategy):
    params = (
        ('logging', True),
        ('longs_enabled', True),
        ('shorts_enabled', True),
        ('stop_loss', 0),
        ('risk_reward', 0),
    )
    
    def __init__(self):
        self.orders_ref = list()
        self.total_profit = 0
        self.initial_cash = self.broker.getcash()
        
        self._init_indicators()
        self.active = True
        
    def _init_indicators(self):
        pass
    
    @abstractmethod
    def _open_short_condition(self) -> bool:
        pass

    @abstractmethod
    def _open_long_condition(self) -> bool:
        pass

    @abstractmethod
    def _close_short_condition(self) -> bool:
        pass

    @abstractmethod
    def _close_long_condition(self) -> bool:
        pass

#Base class for logging    
    # def _log(self, txt):
    #     if self.p.logging:
    #         print(f"{self.datas[0].datetime.datetime(0)}: {txt}")

    def _log(self, txt):
        if self.p.logging:
            try:
                print(f"{self.datas[0].datetime.datetime(0)}: {txt}")
            except:
                print(f"{datetime.now()}: {txt}")
            
    def _log_trade(self, trade):
        self._log(colored('OPERATION PROFIT, GROSS %.2f, NET %.2f'
                      %(trade.pnl, trade.pnlcomm), 'green' if trade.pnl > 0 else 'red'))

    def _log_total_profit(self):
        self._log(colored('TOTAL PROFIT %.2f' % self.total_profit, 'green' if self.total_profit > 0 else 'red'))

    def _log_order(self, order):
        self._log('Order ref: {} / Type {} / Status {}'.format(
            order.ref,
            colored('BUY' if order.isbuy() else 'SELL', 'green' if order.isbuy() else 'red'),
            order.getstatusname()
        ))

    def _log_iter(self):
        self._log(f"Close : {self.datas[0].close[0]}")

    def _log_long_order(self, stop_price, take_profit_price):
        self._log(colored(f"LONG ORDER SIGNAL: Stop loss: {stop_price} / Take profit: {take_profit_price}", 'green'))

    def _log_short_order(self, stop_price, take_profit_price):
        self._log(colored(f"SHORT ORDER SIGNAL: Stop loss: {stop_price} / Take profit: {take_profit_price}", 'red'))

    def _log_start(self):
        self._log(colored('Starting Portfolio Value: %.2f' % self.broker.getvalue(), 'green'))

    def _log_stop(self):
        portfolio_value = self.broker.getvalue()
        total_return_pct = (portfolio_value - self.initial_cash) / self.initial_cash * 100

        portfolio_value_color = 'green' if self.broker.getvalue() > self.initial_cash else 'red'
        total_profit_color = 'green' if self.total_profit > 0 else 'red'
        total_return_color = 'green' if total_return_pct > 0 else 'red'

        self._log(colored('Final Portfolio Value: %.2f' % portfolio_value, portfolio_value_color))
        self._log(colored(f"Total Return: {total_return_pct:.2f}%", total_return_color))
        self._log_total_profit()

#Base class for event functions       
    def notify_data(self, data, status, *args, **kwargs):
        if status == data.LIVE:
            self._log('Data live notification')
            self.active = True
        if status == data.DELAYED:
            self._log('Data delayed notification')
            self.active = False

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self._log_trade(trade)
        self.total_profit += trade.pnlcomm
        self._log_total_profit()

    def notify_order(self, order):
        self._log_order(order)
        self._del_order_if_not_alive(order)

#delete useless orders, such as the stop loss order after the take profit was triggered       
    def _del_order_if_not_alive(self, order):
        if not order.alive() and order.ref in self.orders_ref:
            self.orders_ref.remove(order.ref)

# separate the cases based on whether I already have open orders or not       
    def next(self):
        self._log_iter()

        if not self.active:
            return

        if not self.position:
            self._not_yet_in_market()
        else:
            self._in_market()

# Close positions if the conditions are met ; 
# self.position ensure we close only the resp. long or short          
    def _in_market(self):
        if self._close_long_condition() and self.position.size > 0:
            self.close()
        if self._close_short_condition() and self.position.size < 0:
            self.close()
            
#Check if conditions are valid ; 
# if they are, we have to calculate our orders prices and submit the orders
    def _not_yet_in_market(self):
        if self._long_condition():
            stop_price = self._get_long_stop_loss_price()
            take_profit_price = self._get_long_take_profit_price()

            self._go_long(stop_price, take_profit_price)
            self._log_long_order(stop_price, take_profit_price)

        if self._short_condition():
            stop_price = self._get_short_stop_loss_price()
            take_profit_price = self._get_short_take_profit_price()

            self._go_short(stop_price, take_profit_price)
            self._log_short_order(stop_price, take_profit_price)
    
    def _long_condition(self):
        return self._open_long_condition() and self.params.longs_enabled

    def _short_condition(self):
        return self._open_short_condition() and self.params.shorts_enabled

#set SL & TP to the current price:
#For the order logic adaption of _go_long/_go_short
    def _get_long_stop_loss_price(self) -> float:
        return self.datas[0].close[0]

    def _get_long_take_profit_price(self) -> float:
        return self.datas[0].close[0]

    def _get_short_stop_loss_price(self) -> float:
        return self.datas[0].close[0]

    def _get_short_take_profit_price(self) -> float:
        return self.datas[0].close[0]
    
# submit Long orders to brokers; 
# Depending on the parameters, the system swicth between OCO; limit & stop
    def _go_long(self, stop_price, take_profit_price):
        orders = self._get_long_orders_from_stop_and_take_profit(stop_price, take_profit_price)
        self.orders_ref = [order.ref for order in orders if order]
        self.entry_bar = len(self)
        
    def _get_long_orders_from_stop_and_take_profit(self, stop_price, take_profit_price):
        ACTUAL_PRICE = self.datas[0].close[0]
        if stop_price != ACTUAL_PRICE and take_profit_price != ACTUAL_PRICE:
            orders = self.buy_bracket(price=ACTUAL_PRICE, stopprice=stop_price, limitprice=take_profit_price)
        elif stop_price != ACTUAL_PRICE and take_profit_price == ACTUAL_PRICE:
            orders = [self.buy(), self.sell(exectype=bt.Order.Stop, price=stop_price)]
        elif stop_price == ACTUAL_PRICE and take_profit_price != ACTUAL_PRICE:
            orders = [self.buy(), self.sell(exectype=bt.Order.Limit, price=take_profit_price)]
        else:
            orders = [self.buy()]
        return orders

# submit Short orders to brokers
# Depending on the parameters, the system swicth between OCO; limit & stop

    def _go_short(self, stop_price, take_profit_price):
        orders = self._get_short_orders_from_stop_and_take_profit(stop_price, take_profit_price)
        self.orders_ref = [order.ref for order in orders if order]
        self.entry_bar = len(self)

    def _get_short_orders_from_stop_and_take_profit(self, stop_price, take_profit_price):
        ACTUAL_PRICE = self.datas[0].close[0]
        if stop_price != ACTUAL_PRICE and take_profit_price != ACTUAL_PRICE:
            orders = self.sell_bracket(price=ACTUAL_PRICE, stopprice=stop_price, limitprice=take_profit_price)
        elif stop_price != ACTUAL_PRICE and take_profit_price == ACTUAL_PRICE:
            orders = [self.sell(), self.buy(exectype=bt.Order.Stop, price=stop_price)]
        elif stop_price == ACTUAL_PRICE and take_profit_price != ACTUAL_PRICE:
            orders = [self.sell(), self.buy(exectype=bt.Order.Limit, price=take_profit_price)]
        else:
            orders = [self.sell()]
        return orders

#Initialization steps of strategy   
    def start(self):
        self._log_start()

    def stop(self):
        self._log_stop()