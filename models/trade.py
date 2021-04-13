from enum import Enum
import numpy as np

class TradeDirection(Enum):
    LONG = 1
    #SHORT = -1

class Trade():
    def __init__(self, entry_price : float, quantity : float, direction : TradeDirection, take_profit_pct : float,
                commission_pct : float = 0.001, stop_loss_pct : float = None, leverage : int = 10) -> None:

        self._entry_price = entry_price
        self._direction = direction
        self._take_profit_pct = abs(take_profit_pct)
        self._stop_loss_pct = -abs(stop_loss_pct) if stop_loss_pct is not None else -100
        self._leverage = int(np.clip(leverage, 1, 100))
        self._quantity = quantity
        self._commission_pct = commission_pct

        self.__calc_price_from_pct = lambda pct: self._entry_price * (1 + ((pct / 100) * self._direction.value)) 

        self._take_profit_price = self.__calc_price_from_pct(self._take_profit_pct)
        self._stop_loss_price = self.__calc_price_from_pct(self._stop_loss_pct)

        self._liq_price = self._liquidation_price()

        self.profit = 0

        if direction != TradeDirection.LONG:
            raise NotImplementedError

    def has_closed(self, high, low) -> bool:
        c = self._leverage * self._quantity * self._direction.value / 100

        is_closed = False
        if high >= self._take_profit_price:
            self.profit = self._take_profit_pct * c
            self.profit *= 1 - self._commission_pct
            is_closed = True
        elif low <= self._stop_loss_price:
            self.profit = self._stop_loss_pct * c
            self.profit *= 1 + self._commission_pct
            is_closed = True
        elif low <= self._liq_price:
            self.profit = -self._quantity
            is_closed = True
        else:
            is_closed = False

        return is_closed


    def _liquidation_price(self) -> float:
        return self.__calc_price_from_pct(-100)

    @property
    def profit_pct(self):
        return self.profit / self._quantity


import unittest

class TestTrade(unittest.TestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self.trade = Trade(1000, 1000, TradeDirection.LONG, commission_pct=0.001, take_profit_pct=1, stop_loss_pct=-5)

    def test_calc_take_profit(self):
        self.assertEqual(self.trade._take_profit_price, 1010, "Take profit price should be 1010")

    def test_calc_stop_loss(self):
        self.assertEqual(self.trade._stop_loss_price, 950, "Stop loss price should be 950")

    def test_continuing(self):
        self.assertEqual(self.trade.has_closed(1000, 1000), False)

    def test_close_profit(self):
        close = self.trade.has_closed(2000, 1000)
        self.assertEqual(close, True)
        self.assertEqual(self.trade.profit, 99.9)
        self.assertEqual(self.trade.profit_pct, 0.0999)

    def test_close_loss(self):
        close = self.trade.has_closed(1000, 500)
        self.assertEqual(close, True)
        self.assertEqual(self.trade.profit, -500.49999999999994)
        self.assertEqual(self.trade.profit_pct, -0.5005)

    # def test_close_liquidation(self):
    #     self.trade._stop_loss_price = 0
    #     close = self.trade.has_closed(1000, 100)
    #     self.assertEqual(close, True)
    #     self.assertEqual(self.trade.profit, -1000)
    #     self.assertEqual(self.trade.profit_pct, -1)

if __name__ == '__main__':
    unittest.main()