from abc import ABC, abstractmethod
import pandas as pd
import datetime as dt
from Data.timeframes import Timeframes

class DataSource(ABC):

    def get_data(self, backtest_parameters):
        start_date = backtest_parameters.get('start_date', dt.datetime(2019, 1, 1))
        duration = backtest_parameters.get('duration', 500)
        timeframe = backtest_parameters.get('timeframe', Timeframes.d1)
        symbol = backtest_parameters.get('symbol', 'BTC/USDT')

        print(f'Getting data for {symbol} from {start_date} for {duration} ticks with {timeframe.name} timeframe with {self.__class__.__name__} data source')
        return self._get_data(self._get_symbol(symbol), self._get_start_date(start_date), self._get_duration(duration), self._get_timeframe(timeframe))

    @abstractmethod
    def _get_data(self, symbol, start_date, duration, timeframe) -> pd.DataFrame:
        pass

    def _get_symbol(self, symbol):
        return symbol

    def _get_start_date(self, start_date):
        return start_date

    def _get_duration(self, duration):
        return duration

    def _get_timeframe(self, timeframe):
        return timeframe