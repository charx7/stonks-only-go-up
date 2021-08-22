import logging
import math
import numpy as np


logging.basicConfig(filename='output.log', filemode='a',
  format='%(asctime)s - %(levelname)-4s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)


class BackTester():
  def __init__(self, data, initial_period, window_size):
    self.data = data
    self._rts = data.pct_change()
    self._data_generator = self.df_generator()  # data generator that will be used to traverse the df with the next method
    self._generator_iteration = 0
    
    self.initial_period = initial_period
    self.window_size = window_size
    
    self.log = None
    
    # portfolio based properties
    self.initial_capital = 100
    self.weights_df = self._rts.copy()
    
  def df_generator(self):
    window_selection = 0 + self.initial_period  # initial selection of the data
    while(True):
      yield self.data.iloc[:window_selection,:]
      window_selection += self.window_size  # advance the generator one window size
      self._generator_iteration += 1
            
  def set_strategy(self, strategy):
    self.strategy = strategy  # you'd need to overwrite strategy before instantiating the class
    
  def compute_metrics(self, weights):
    self.enr_df = weights.merge(self.weights_df, left_index=True, right_index=True) # join with the data

    # this gets called everytime you compute the metrics should be only once at the end
    self.enr_df["portfolio_daily_returns"] = self.enr_df.apply(lambda row: np.dot(np.array(row[:1][0]), row[1:len(self.data.columns) + 1].values), axis = 1)
    self.enr_df["cumulative_returns"] = (self.enr_df["portfolio_daily_returns"] + 1).cumprod()

  def next_per(self):
    assert self.strategy != None, "Set a strategy first"
    next_df = next(self._data_generator)
    logging.info(f"Setting the data with shape: {next_df.shape}, generator iteration {self._generator_iteration}")
    self.strategy.set_period_data(next_df)
    self.strategy.execute()
        
    if self.strategy.strat_executed:
      weights = self.strategy.weights
      self.compute_metrics(weights)
    
  def backtest(self):
    n_windows = math.ceil(self.data.shape[0] / self.window_size)
    print(n_windows)
        
    for _ in range(n_windows)[:2]:
        self.next_per()
