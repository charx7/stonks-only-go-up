import logging
import pandas as pd


from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import objective_functions 


logging.basicConfig(filename='output.log', filemode='a',
  format='%(asctime)s - %(levelname)-4s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)


class AssetAllocation:
  def __init__(self, expected_returns: pd.Series = pd.Series(), covar_matrix: pd.DataFrame = pd.DataFrame(),
     allocation_stategy: str = "") -> None:
      # class properties
      self.strategy = allocation_stategy
      self.expected_returns = expected_returns
      self.covar_matrix = covar_matrix

      # allocation properties
      self.ef = None  # efficient frontier
      self.weights = None  # portfolio weights
      self.portfolio_perf = None  # portfolio performance

      if self.strategy == "markowitz-regularized":
        self.ef, self.weights, self.portfolio_perf = self.markowitz_regularized(self.expected_returns, self.covar_matrix)


  @staticmethod
  def markowitz_regularized(mu, S):
    logging.info(f"Computing asset allocations using: Markowitz regularized")
    ef = EfficientFrontier(mu, S)
    ef.add_objective(objective_functions.L2_reg)  # L2 regularization of the objective function

    ef.max_sharpe()
    weights = ef.clean_weights()
    port_perf = ef.portfolio_performance(verbose=True)

    return ef, weights, port_perf
