import yfinance as yf
import pandas as pd
import logging

from pypfopt import black_litterman
from pypfopt.expected_returns import mean_historical_return
from pypfopt.black_litterman import BlackLittermanModel
from pypfopt.risk_models import CovarianceShrinkage
from typing import Dict, List


logging.basicConfig(filename='output.log', filemode='a',
  format='%(asctime)s - %(levelname)-4s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)


class MarketModels:
  def __init__(self, historical_prices: pd.DataFrame, model: str, views_dict: Dict[str, float] = {},
    confidences: List[float] = [], mcaps: pd.DataFrame = pd.DataFrame()) -> None:
    self.historical_prices_df = historical_prices  # they have to be backfilled

    # data validation for views and confidences
    assert len(views_dict) == len(confidences), "Views and confidences need to be of the same size"
    self.views_dict = views_dict
    self.confidences = confidences

    self.S = None  # covar matrix historical
    self.mu = None  # mean historical returns

    # get the market prices for the sp500 -> main index asset
    logging.info(f"Initiating download of the main index: 'sp500'")
    self.sp500 = yf.download("SPY", period="max")["Adj Close"]

    # bl params
    self.delta = None  # market implied risk aversion
    self.market_prior = None  # compute the market priors -> this needs to be done according to a parameter
    self.mcaps = mcaps
    #self.market_prior = self.market_priors(self.mkt_data_reader.mcaps, self.delta, self.S)

    if model == "bl":
      logging.info(f"Computing the expected returns and covar matrices given the Black-Litterman model")
      #mu_prior = self.compute_estimated_returns(self.historical_prices_df)
      S_prior = self.covar_matrix(self.historical_prices_df)
      self.S = S_prior
      # delta compute the market implied risk aversion parameter
      self.delta = black_litterman.market_implied_risk_aversion(self.sp500)

      self.market_prior = self.market_priors(self.mcaps, self.delta, S_prior)

      bl, ret_bl, S_bl = self.black_litterman(S_prior, self.market_prior, self.delta, self.views_dict, self.confidences)
      self.model = {
        "name": "Black-litterman",
        "model": bl
      }
      self.ret_bl = ret_bl # mean matrix for black litterman
      self.S_bl = S_bl # co-variance matrix for black litterman


  @staticmethod
  def black_litterman(S, market_prior, delta, viewdict, confidences):
    # bl model
    bl = BlackLittermanModel(
      S,
      pi = market_prior,
      absolute_views = viewdict,
      risk_aversion = delta,
      omega = "idzorek",
      view_confidences = confidences
    )
    
    ret_bl = bl.bl_returns() # mean matrix for black litterman
    S_bl = bl.bl_cov() # co-variance matrix for black litterman

    return bl, ret_bl, S_bl


  @staticmethod
  def compute_estimated_returns(mkt_data):
    logging.info(f"Computing estimated returns using: 'mean_historical_return'")
    return mean_historical_return(mkt_data)


  @staticmethod
  def covar_matrix(mkt_data):
    logging.info(f"Computing the sample covariance matrix using: Ledoit-Wolf shrinkage")
    return CovarianceShrinkage(mkt_data).ledoit_wolf()


  @staticmethod
  def market_priors(mcaps, delta, S):
    logging.info(f"Computing the market implied prior returns using: mcaps, (delta) market implied risk aversion, (S) sample covar matrix")
    return black_litterman.market_implied_prior_returns(mcaps, delta, S)
