import pandas as pd

class StockDataFrame():
    def __init__(self, filename : str) -> None:
        self.df = pd.read_csv(filename, index_col=0)

    @property
    def current_ohlc(self) -> tuple:
        raise NotImplementedError

    @property
    def max_price(self) -> float:
        raise NotImplementedError

    @property
    def state_shape(self) -> tuple:
        raise NotImplementedError

    def next(self) -> tuple:
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError
