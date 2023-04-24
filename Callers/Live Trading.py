import backtrader as bt
from ccxtbt import CCXTStore
import time

from Trading_bot.tradingBot import TradingBot

from Account_management.GetAPIKeys import GetAPIKeys

from Strategy.BuyHoldwithBracket import BuyHoldStrategy
from Strategy.Base_Strategy_simplified import TestStrategy
from Strategy.EMAwithBracket import EMAStrategyExample

import Others.LoggerAPI as logger
# logger.debug_requests_on()

sandbox = True
exchange='binance'

credential = GetAPIKeys().getAPIkeys(exchange, sandbox)
api_key = credential['User']
api_secret = credential['Password']


store1 = CCXTStore(
    exchange=exchange,
    currency='USDT',
    config={
        'apiKey': api_key,
        'secret': api_secret,
        'nonce': lambda: str(int(time.time() * 1000)),
        'enableRateLimit': True,
        'adjustForTimeDifference': True,
        'newOrderRespType': 'FULL',
        'defaultTimeInForce': 'GTC',
        'verbose': False
    },
    retries=1,
    sandbox=sandbox,
    debug=True
)


# store2 = CCXTStore(
#     exchange=exchange,
#     currency='USDT',
#     config={
#         'apiKey': api_key,
#         'secret': api_secret,
#         'nonce': lambda: str(int(time.time() * 1000)),
#         'enableRateLimit': True,
#         'adjustForTimeDifference': True,
#         'newOrderRespType': 'FULL',
#         'defaultTimeInForce': 'GTC',
#         'verbose': True
#     },
#     retries=1,
#     sandbox=sandbox,
#     debug=True
# )



bot = TradingBot()

# strategy = TestStrategy
# strategy_parameters = {}


strategy = EMAStrategyExample
strategy_parameters = {
    'period_me1': 12, 'logging': True, 'stop_loss': 1, 
}

# strategy = BuyHoldStrategy
# strategy_parameters = {
#     'logging': True, 'stop_loss': 0.015, 'risk_reward': 3
# }

sizer = bt.sizers.PercentSizer
sizer_parameters = {
    'percents': 1
}

analyzers = [
    bt.analyzers.TradeAnalyzer
    ]


live_parameters = {
    'dataname': 'BTC/USDT',
    'name': "BTCUSDT",
    'timeframe': bt.TimeFrame.Minutes,
    'timeDeltaMin': 50,
    'compression':1,
    'ohlcv_limit':50,
    'drop_newest':True
}
result, cerebro =bot.live(strategy, live_parameters, store=store1, strategy_parameters=strategy_parameters, sizer=sizer,
         sizer_parameters=sizer_parameters, analyzers=analyzers)
         
strat_result = result[0]
analysis = strat_result.analyzers.TradeAnalyzer.get_analysis()
    # total_net_pnl = analysis.pnl.net.total
    # print(f"Parameters: {params} | Total Net PNL: {total_net_pnl}")        
    
cerebro.plot()
