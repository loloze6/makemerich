import ccxt
from Data.data_sources import DataSource
import pandas as pd


class CCXT_DATA(DataSource):
    def _get_timeframe(self, timeframe):
        try:
            timeframe = timeframe.name[-1] + timeframe.name[:-1]
            if timeframe not in ['1m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']:
                raise ValueError
            return timeframe
        except ValueError:
            raise ValueError(f'CCXT does not support {timeframe} timeframe')

    def _get_symbol(self, symbol):
        try:
            ticker = ccxt.binance().fetchTicker(symbol)
            if not ticker.get('bid', None):
                raise ValueError
            return symbol
        except ValueError as e:
            raise ValueError(f'CCXT does not support {symbol} symbol')

    def _get_start_date(self, start_date):
        start_date=ccxt.binance().parse8601(start_date)
        return start_date
       
    def _get_data(self, symbol, start_date, duration, timeframe):
        data = ccxt.binance().fetch_ohlcv(symbol, since=start_date, limit=duration, timeframe=timeframe)
        data = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data.set_index('timestamp', inplace=True)
        return data
