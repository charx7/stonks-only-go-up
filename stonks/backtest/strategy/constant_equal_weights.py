import pandas as pd
import logging

from stonks.backtest.strategy.base_strat import BaseStrategy


logging.basicConfig(filename='output.log', filemode='a',
  format='%(asctime)s - %(levelname)-4s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)


class EqualWeightsStrategy(BaseStrategy):    
    # override of the abstract method
  def execute(self):
    if self.curr_period_data.empty == False:
      self.log()
      self.set_weights()
      self.compute_returns()            
      self.strat_executed = True

  def set_weights(self):
    dts = self.curr_period_data.index
    n = len(self.curr_period_data.columns)
    weights_lst = [1/n for _ in range(n)]
    weights_lst_rep = [weights_lst for _ in range(len(dts))]

    self.weights = pd.DataFrame(
        {
            'weights': weights_lst_rep
        },
        index = dts
    )

  def compute_returns(self):
    self.rets = self.curr_period_data.pct_change().iloc[1:,:]

  def log(self):
    logging.info(f"The shape of the current data is: {self.curr_period_data.shape}")
    logging.info(f"Dt from: {self.curr_period_data.index[0].strftime('%Y-%m-%d')} to: {self.curr_period_data.index[-1].strftime('%Y-%m-%d')}") if self.curr_period_data.empty != True else print("The DF is empty")
        