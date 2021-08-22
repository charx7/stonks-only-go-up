import logging
import pandas as pd

from abc import ABC, abstractmethod


logging.basicConfig(filename='output.log', filemode='a',
  format='%(asctime)s - %(levelname)-4s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)


class BaseStrategy(ABC):
  def __init__(self):
      # ideally this should be an abstract property
      self.strat_executed = False
      self.weights = None
  
  @abstractmethod
  def execute(self):
      pass
  
  def execute_strategy(self):
      self.execute()
  
  def set_period_data(self, curr_period_data):
      self.curr_period_data = curr_period_data
  