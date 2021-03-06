from abc import ABC
from typing import Iterable, List
import gym
from gym import error, spaces, utils
from gym.utils import seeding

import random

import pandas as pd
import numpy as np

from models.trade import Trade, TradeDirection
from models.stock_df import StockDataFrame
from utils.logger import Logger

class FuturesStockEnv(gym.Env, ABC):
    metadata = {'render.modes': ['human']}

    def __init__(self, initial_capital: float, take_profit_pct : float, stop_loss_pct : float, commission_pct : float, order_size_pct : float, 
                    stocks_df : Iterable[StockDataFrame], base_currency : str = 'USD'):
        super(FuturesStockEnv, self).__init__()

        self.initial_capital = initial_capital
        self.balance = self.initial_capital

        self.commission_pct = commission_pct / 100.0
        self.order_size = order_size_pct / 100.0
        self.take_profit_pct = take_profit_pct
        self.stop_loss_pct = stop_loss_pct

        self.base_currency = base_currency
        self.stocks_df = stocks_df
        self.trades : List[Trade] = []

        self.current_stock_df : StockDataFrame = random.choice(self.stocks_df)
        self.current_trade : Trade = None

        self.observation_space = spaces.Box(low=0, high=self.current_stock_df.max_price, shape=self.current_stock_df.state_shape)
        self.action_space = spaces.Box(low=0, high=1, shape=(1,))

    def step(self, action : float):
        reward = 0
        
        state, done = self.current_stock_df.next()

        _, high, low, close = state[-1][:4]

        quantity = self.balance * self.order_size
        if self.current_trade is not None and self.current_trade.has_closed(high, low):
            if self.current_trade.profit == -quantity:
                reward = -self.balance
                done = True
                Logger().info('Liquidation')
            else:
                self.balance += self.current_trade.profit
                reward = self.current_trade.profit
                Logger().info(f'Close at {self.__progress}% with profit: {self.current_trade.profit}')
            self.current_trade = None
        elif action > 0.85 and self.current_trade is None:
            entry_price = close
            direction = TradeDirection.LONG
            self.current_trade = Trade(entry_price, quantity, direction, 
                                        take_profit_pct=self.take_profit_pct, 
                                        stop_loss_pct=self.stop_loss_pct, leverage=10)
            self.trades.append(self.current_trade)
            Logger().info(f'Open long at {self.__progress}% balance: {self.balance}')
        else:
            reward = -1

        if self.balance <= self.initial_capital * 0.1:
            reward = -(self.initial_capital-self.balance)
            done = True
            Logger().info('Game Over')

        if done and reward > 0:
            reward *= self.sharp_ratio

        return state, reward, done, None

    @property
    def __progress(self):
        return int(self.current_stock_df.current_index / len(self.current_stock_df.df) * 100)

    def reset(self):
        Logger().info('Reset')
        self.current_stock_df.reset()

        self.current_stock_df = random.choice(self.stocks_df)
        state, _ = self.current_stock_df.next()
        self.balance = self.initial_capital
        self.trades = []
        self.current_trade = None
        return state

    def render(self, mode='human', close=False):
        pass

    @property
    def max_drawndown(self):
        if len(self.trades) == 0:
            return 1
        bal = np.cumsum([t.profit for t in self.trades]) + self.initial_capital
        return min(np.diff(bal) / bal[1:] * 100) + np.finfo(np.float32).eps

    @property
    def sharp_ratio(self):
        excess_returns : np.ndarray = np.array([t.profit_pct for t in self.trades]) - 0.018
        return excess_returns.mean() / excess_returns.std()