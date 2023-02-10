import backtrader as bt
import ccxt
from Trading_bot_tuto.tradingBot import TradingBot
from Trading_bot_tuto.timeframes import Timeframes
from Trading_bot_tuto.ccxt_data import CCXT_DATA

bot = TradingBot()
data_source=CCXT_DATA()

backtest_parameters = {
    'start_date': 1514764800000,
    'duration': 200,
    'timeframe': Timeframes.d1,
    'symbol': 'BTC/USDT',
    'initial_cash': 10000,
    'commission': 0.001,
    'slippage': 0.001
}

strategy = bt.strategies.MA_CrossOver
strategy_parameters = {
    'fast': range(10, 15),
}


sizer = bt.sizers.PercentSizer
sizer_parameters = {
    'percents': 99
}

analyzers = [
    bt.analyzers.TradeAnalyzer
    ]

results = bot.backtest(strategy, backtest_parameters, data_source, strategy_parameters=strategy_parameters, sizer=sizer,
                       sizer_parameters=sizer_parameters, analyzers=analyzers)
for result in results:
    print(f"Net profit: {result[0].analyzers.tradeanalyzer.get_analysis()['pnl']['net']['total']}")