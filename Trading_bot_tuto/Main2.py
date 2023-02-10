import backtrader as bt
import ccxt
from Trading_bot_tuto.tradingBot import TradingBot
from Trading_bot_tuto.timeframes import Timeframes
from Trading_bot_tuto.ccxt_data import CCXT_DATA
from Trading_bot_tuto.CustomStrategy import BracketStrategyExample
bot = TradingBot()
data_source=CCXT_DATA()

backtest_parameters = {
    'start_date': '2019-01-01T00:00:00Z',
    'duration': 1000,
    'timeframe': Timeframes.m5,
    'symbol': 'BTC/USDT',
    'initial_cash': 10000,
    'commission': 0.001,
    'slippage': 0.001
}

# strategy = bt.strategies.MA_CrossOver
# strategy_parameters = {
#     'fast': range(10, 15),
# }
strategy = BracketStrategyExample
strategy_parameters = {
    'period_me1': 12, 'logging': True, 'stop_loss': range(1, 3), 'risk_reward': range(1, 5)
}


sizer = bt.sizers.PercentSizer
sizer_parameters = {
    'percents': 99
}

analyzers = [
    bt.analyzers.TradeAnalyzer
    ]

results, cerebro= bot.backtest(strategy, backtest_parameters, data_source, strategy_parameters=strategy_parameters, sizer=sizer,
                       sizer_parameters=sizer_parameters, analyzers=analyzers)
for result in results:
    print(f"Net profit: {result[0].analyzers.tradeanalyzer.get_analysis()['pnl']['net']['total']}")

