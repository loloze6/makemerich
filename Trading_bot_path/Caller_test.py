import backtrader as bt
from DataFunctions import fetchData

from Trading_bot_path.Custom_indicator import DelayedPrice

from Trading_bot_path.Doji_strategy import Doji_strategy
from Trading_bot_path.EMA_Strategy import EMA_strategy
from Trading_bot_path.BracketStrategy import BracketStrategy

from Trading_bot_path.Custom_analyzer import CustomAnalyzer

import Trading_bot_path.Custom_observer as Observer

data=fetchData(token='ETH/USDT',barDuration='15m',start='2018-01-01T00:00:00Z', duration = 500)
dataBT=data['BT_DataFeed']

def backtest_strategy_non_optimized(strategy, data, analyzers=None, **parameters):
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    #cerebro.addindicator(DelayedPrice)
    if not analyzers:
        analyzers = []
    for analyzer in analyzers:
        cerebro.addanalyzer(analyzer, _name=analyzer.__name__.lower())
        print(analyzer)
    cerebro.broker.setcash(100_000)
    cerebro.broker.setcommission(commission=0.001) # 0.1%
    cerebro.broker.set_slippage_perc(0.001) # 0.1%
    cerebro.addstrategy(strategy, **parameters)
    result=cerebro.run(stdstats=False)
    return result, cerebro

#result=backtest_strategy_non_optimized(MyStrategy, dataBT, analyzers=[bt.analyzers.TradeAnalyzer])
result, cerebro=backtest_strategy_non_optimized(
    Doji_strategy, 
    dataBT, 
    analyzers=[CustomAnalyzer]
    )
print(result[0].analyzers.customanalyzer.get_analysis())
cerebro.addobserver(bt.observers.TimeReturn)
cerebro.addobserver(Observer.BrokerObserver)
cerebro.addobserver(Observer.TradeObserver)
cerebro.addobserver(Observer.OrderObserver)
cerebro.run()
cerebro.plot(
    style='candlestick',
    volume=False,
    grid=False,
    barup='green',
    bardown='red'
    )

if __name__ == '__main__':
    result, cerebro=backtest_strategy_non_optimized(
        BracketStrategy, 
        dataBT, 
        analyzers=[CustomAnalyzer],
        stop_loss=1,
        take_profit=2
    )
    print(result[0].analyzers.customanalyzer.get_analysis())
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

def backtest_strategy_optimized(strategy, data, analyzers=None **parameters):
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    if not analyzers:
        analyzers = []
    for analyzer in analyzers:
        cerebro.addanalyzer(analyzer, _name=analyzer.__name__.lower())
    cerebro.broker.setcash(100_000)
    cerebro.broker.setcommission(commission=0.001) # 0.1%
    cerebro.broker.set_slippage_perc(0.001) # 0.1%
    cerebro.optstrategy(strategy, **parameters)
    #result = cerebro.run(maxcpus=1, optreturn=True)
    result = cerebro.run(maxcpus=1, optreturn=False)
    #return result
    return result, cerebro

def get_params_from_strategy_result(strategy_result):
    params = strategy_result.params
    return dict(params._getkwargs())

#EMA optim
#result, cerebro = backtest_strategy_optimized(MyStrategy, dataBT, ema_period=range(5, 11))

result, cerebro = backtest_strategy_optimized(Doji_strategy, dataBT, doji_threshold=range(1, 5))

#result = backtest_strategy_optimized(MyStrategy, dataBT, ema_period=range(5, 11))
for res in result:
    strat_result = res[0]
    params = get_params_from_strategy_result(strat_result)
    analysis = strat_result.analyzers.trade.get_analysis()
    total_net_pnl = analysis.pnl.net.total
    print(f"Parameters: {params} | Total Net PNL: {total_net_pnl}")

cerebro.plot()
    
