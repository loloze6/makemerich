import time
import backtrader as bt
import datetime as dt
import ccxt
import cryptocmd

from ccxtbt import CCXTStore

store = CCXTStore(
    exchange='binance',
    currency='USD',
    config={
        'apiKey': 'test',
        'secret': 'test',
        'nonce': lambda: str(int(time.time() * 1000)),
        'enableRateLimit': True,
    },
    sandbox=sandbox
)