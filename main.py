import random
import numpy as np
from tqdm import tqdm
import pandas as pd
from preprocessing.indicators import IndicatorsPreprocessor, PriceSource
from preprocessing.resampler import TimeResamplerPreprocessor
from preprocessing.datetime_decomposition import DateTimePreprocessor
from preprocessing import Preprocessor
from models.stock_df import StockDataFrame
from gym_env.futures_stock_env import FuturesStockEnv
from typing import List
from agents.algorithmic_strategy.sma_agent import SMAgent
import pyswarms as ps
from itertools import product
import joblib

times = ['10T', '15T', '20T', '25T', '30T', '40T', '45T', '50T', '55T', '1H', '70T', '80T', '90T', '2H']

PROCESS = 8

def optimize_strategy(x):
    time_index, period_fastSMA, period_slowSMA, take_profit, stop_loss = x

    preprocessors : List[Preprocessor] = [
        TimeResamplerPreprocessor(time_index),
        IndicatorsPreprocessor().sma(int(period_fastSMA), name='fastSMA')
                                .sma(int(period_fastSMA) + int(period_slowSMA), name='slowSMA')
    ]

    dfs : List[StockDataFrame] = StockDataFrame.load_all_from_folder('datasets', preprocessors=preprocessors)
    agent = SMAgent()

    score = []
    for stock_df in dfs:
        stock_env = FuturesStockEnv(initial_capital=1500, take_profit_pct=take_profit, stop_loss_pct=stop_loss, commission_pct=0.1, order_size_pct=70, stocks_df=[stock_df])

        done = False
        cum_reward = 0
        state = stock_env.reset()

        while not done:
            state, reward, done, _ = stock_env.step(agent.action(state))
            cum_reward += reward

        score.append(stock_env.balance * stock_env.sharp_ratio / stock_env.max_drawndown)

    return -np.mean(score)

if __name__ == '__main__':
    # period_fastSMA = np.linspace(2, 30, num=30, dtype=int)
    # period_slowSMA = np.linspace(2, 20, num=20, dtype=int)
    # take_profit = np.linspace(1, 4, num=10, dtype=float)
    # take_profit = np.linspace(1, 6, num=10, dtype=float)

    # combinations = list(product(times, period_fastSMA, period_slowSMA, take_profit, take_profit))
    # random.shuffle(combinations)

    # scores = []
    # try:
    #     for c in tqdm(combinations):
    #         scores.append((optimize_strategy(c), c))
    # except KeyboardInterrupt:
    #     pass

    # print(scores)

    # print('Saving...')
    # joblib.dump(scores, 'scores')

    # max_bound = (len(times), 50, 15, 4, 6)
    # min_bound = (0, 2, 2, 1, 1)
    # bounds = (min_bound, max_bound)
    # options = {'c1': 0.5, 'c2': 0.3, 'w':0.9}

    # optimizer = ps.single.GlobalBestPSO(n_particles=1, dimensions=len(max_bound), bounds=bounds, options=options)

    # cost, pos = optimizer.optimize(optimize_strategy, iters=250, n_processes=None)

    # print('Time', times[int(pos[0])])
    # print('fastSMA', int(pos[1]))
    # print('slowSMA', int(pos[1]) + int(pos[2]))
    # print(f'take_profit {round(pos[3], ndigits=2)}%')
    # print(f'stop_loss {round(pos[4], ndigits=2)}%')




    preprocessors : List[Preprocessor] = [
        TimeResamplerPreprocessor('80T'),
        IndicatorsPreprocessor().sma(21, name='fastSMA')
                                .sma(21+19, name='slowSMA')
    ]

    dfs : List[StockDataFrame] = StockDataFrame.load_all_from_folder('datasets', preprocessors=preprocessors)
    agent = SMAgent()

    stock_env = FuturesStockEnv(initial_capital=1500, take_profit_pct=1, stop_loss_pct=6, commission_pct=0.1, order_size_pct=70, stocks_df=dfs)

    done = False
    cum_reward = 0
    state = stock_env.reset()

    while not done:
        state, reward, done, _ = stock_env.step(agent.action(state))
        cum_reward += reward

    print('Balance', stock_env.balance)
    print('Max Drawndown', stock_env.max_drawndown)
    print('Sharpe Ratio', stock_env.sharp_ratio)