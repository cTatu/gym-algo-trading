import numpy as np

class SMAgent:
   
   def action(self, state):
      fastSMA, slowSMA = state[:, 4], state[:, 5]

      past_fastSMA, curent_fastSMA = fastSMA
      past_slowSMA, curent_slowSMA = slowSMA

      if curent_fastSMA > curent_slowSMA and past_fastSMA < past_slowSMA:
         return 1
      return 0