from typing import List
from preprocessing import Preprocessor
import pandas as pd
from enum import Enum
import talib

class PriceSource(Enum):
    OPEN = 'Open'
    HIGH = 'High'
    LOW = 'Low'
    CLOSE = 'Close'

class IndicatorsPreprocessor(Preprocessor):
    def __init__(self) -> None:
        self.columns_changes = {}

    def _add_change(self, df : pd.DataFrame) -> pd.DataFrame:
        for col_name, series_fn in self.columns_changes.items():
            df[col_name] = series_fn(df)
        return df

    @property
    def prefix(self) -> str:
        return 'indicator'

    def sma(self, timeperiod : int, source : PriceSource = PriceSource.CLOSE):
        self.columns_changes['SMA'] = lambda df: talib.SMA(df[source.value], timeperiod)
        return self

    def rsi(self, timeperiod : int, source : PriceSource = PriceSource.CLOSE):
        self.columns_changes['RSI'] = lambda df: talib.RSI(df[source.value], timeperiod)
        return self