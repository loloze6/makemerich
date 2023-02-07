import backtrader as bt
from DataFunctions import fetchData
from backtrader.indicators import ExponentialMovingAverage as EMA
from termcolor import colored

data=fetchData(token='ETH/USDT',barDuration='15m',start='2018-01-01T00:00:00Z', duration = 700)
dataBT=data['BT_DataFeed']

class MyStrategy(bt.Strategy):
    params = (
        ('ema_period', 10),
    )

    def __init__(self):
       self.ema = EMA(period=self.p.ema_period)

    def log(self, msg, dt=None):
        print("{} - {}".format(dt or self.datas[0].datetime.date(0), msg))
    def next(self):
        #self.log('{} - {} {} @ {}'.format(self.datas[0].datetime.date(0), self.datas[0].close[0], self.datas[0]._name, self.ema[0]))
        self.log('Close: {}, EMA: {}'.format(self.datas[0].close[0], self.ema[0]))
        if not self.position:

            if self.datas[0].close[0] < self.ema[0]:
                orders = [self.buy()]
                #orders = [self.buy(), self.sell(exectype=bt.Order.Stop, price=stop_price)]
    # or
                #orders = [self.buy(), self.sell(exectype=bt.Order.Limit, price=take_profit_price)]
    # or 
                #orders = self.buy_bracket(price=ACTUAL_PRICE, stopprice=stop_price, limitprice=take_profit_price)

                self.orders_ref = [order.ref for order in orders if order]

        if self.datas[0].close[0] > self.ema[0]:
            self.close()
        #print(self.datas[0].close[-1])
        #print(self.datas[0].volume[0])
        #print(self.datas[0].open[0])
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

            # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

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

def backtest_strategy_non_optimized(strategy, data, **parameters):
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade')
    cerebro.broker.setcash(100_000)
    cerebro.broker.setcommission(commission=0.001) # 0.1%
    cerebro.broker.set_slippage_perc(0.001) # 0.1%
    cerebro.addstrategy(strategy, ema_period=200)
    result=cerebro.run()
    return result

result=backtest_strategy_non_optimized(MyStrategy, dataBT, ema_period=10)

#We run only one strategy, so our strategy’s result is stored in result[0]
strategy_result = result[0]
#We retrieve our analyzer named trade
trade_analyzer = strategy_result.analyzers.trade
#We call get_analysis() to get the analysis from our analyzer
analysis = trade_analyzer.get_analysis()
#print(analyzis)
#We only select a few of them
pnl_net_total = analysis.pnl.net.total
pnl_gross_total = analysis.pnl.gross.total
commissions = pnl_gross_total - pnl_net_total

winners = analysis.won.total
losers = analysis.lost.total
win_rate = winners / (winners + losers) * 100

print("---ANALYSIS---")
print("PnL net total: {}".format(pnl_net_total))
print("PnL gross total: {}".format(pnl_gross_total))
print("Commissions: {}".format(commissions))
print("Win rate: {}".format(win_rate))

cerebro.plot()
