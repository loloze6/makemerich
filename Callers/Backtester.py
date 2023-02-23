import backtrader as bt
from Trading_bot.tradingBot import TradingBot
from Data.timeframes import Timeframes
from Data.ccxt_data import CCXT_DATA
from Strategy.EMAwithBracket import BracketStrategyExample
from Strategy.BuyHoldwithBracket import BuyHoldStrategy


bot = TradingBot()
data_source=CCXT_DATA()

backtest_parameters = {
    'start_date': '2021-01-01T00:00:00Z',
    'duration': 720,
    'timeframe': Timeframes.m1,
    'symbol': 'BNB/USDT',
    'initial_cash': 10000,
    'commission': 0.001,
    'slippage': 0.001
}

# strategy = bt.strategies.MA_CrossOver
# strategy_parameters = {
#     'fast': range(10, 15),
# }
# strategy = BracketStrategyExample
# strategy_parameters = {
#     'period_me1': 12, 'logging': False, 'stop_loss': range(1, 3), 'risk_reward': range(1, 5)
# }


strategy = BuyHoldStrategy
strategy_parameters = {
    'logging': True, 'stop_loss': 1, 'risk_reward': 4
}

sizer = bt.sizers.PercentSizer
sizer_parameters = {
    'percents': 1
}

analyzers = [
    bt.analyzers.TradeAnalyzer
    ]

results, cerebro= bot.backtest(strategy, backtest_parameters, data_source, strategy_parameters=strategy_parameters, sizer=sizer,
                       sizer_parameters=sizer_parameters, analyzers=analyzers)
for result in results:
    print(f"Net profit: {result[0].analyzers.tradeanalyzer.get_analysis()['pnl']['net']['total']}")

