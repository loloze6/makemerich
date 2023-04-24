import backtrader as bt
from Trading_bot.tradingBot import TradingBot
from Data.timeframes import Timeframes
from Data.ccxt_data import CCXT_DATA_BINANCE, CCXT_DATA_BYBIT
from Strategy.EMAwithBracket import EMAStrategyExample
from Strategy.Base_Strategy_simplified import TestStrategy
from Strategy.BuyHoldwithBracket import BuyHoldStrategy


bot = TradingBot()
data_source=CCXT_DATA_BINANCE()

backtest_parameters = {
    'start_date': '2023-01-01T00:00:00Z',
    'duration': 850, #12hours =720min + 130min prep data
    'timeframe': Timeframes.m5,
    'symbol': 'BTC/USDT',
    'initial_cash': 100,
    'commission': 0.1/100,
    'slippage': 0.01/100
}

# strategy = bt.strategies.MA_CrossOver
# strategy_parameters = {
#     'fast': 10,
# }
strategy = EMAStrategyExample
strategy_parameters = {
    'period_me1': 12,
    'period_me2': 26,
    'period_signal': 9,
    'logging': True,
    'stop_loss': 1,
    'shorts_enabled': False #Must be true if no stop_loss in SPOT ; Can be true in Future
    #When OCO will be supported at Binance 'risk_reward': 1
}

# strategy = TestStrategy
# strategy_parameters = {}

# strategy = BuyHoldStrategy
# strategy_parameters = {
#   'logging': False,
#   'stop_loss': 0.5, 
#   'risk_reward': 1
# }



sizer = bt.sizers.PercentSizer
sizer_parameters = {
    'percents': 99
}

analyzers = [
    bt.analyzers.TradeAnalyzer
    ]

results, cerebro= bot.backtest(strategy, backtest_parameters, data_source, strategy_parameters=strategy_parameters, sizer=sizer,
                       sizer_parameters=sizer_parameters, analyzers=analyzers)
# for result in results:
#     print(f"Net profit: {result[0].analyzers.tradeanalyzer.get_analysis()['pnl']['net']['total']}")

cerebro.plot()