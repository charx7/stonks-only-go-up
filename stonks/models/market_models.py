import logging
import copy
import yfinance as yf
import pandas as pd
import numpy as np
import pandas as pd


from pypfopt import black_litterman
from pypfopt.expected_returns import mean_historical_return
from pypfopt.black_litterman import BlackLittermanModel
from pypfopt.risk_models import CovarianceShrinkage
from sklearn.linear_model import LinearRegression
from typing import Dict, List


logging.basicConfig(filename='output.log', filemode='a',
  format='%(asctime)s - %(levelname)-4s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)


class MarketModels:
  def __init__(self, historical_prices: pd.DataFrame, model: str, views_dict: Dict[str, float] = {},
    confidences: List[float] = [], mcaps: pd.DataFrame = pd.DataFrame(),
    ff_factors_df: pd.DataFrame = pd.DataFrame()) -> None:
    self.historical_prices_df = historical_prices  # they have to be backfilled
    self.tickers = list(historical_prices.columns)  # tickers lst

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

    # ff params
    self.ff_factors = ff_factors_df  # ff factors df (can get them form the dr class)
    self.df_stocks_ff = None
    self.risk_factors = list(self.ff_factors.columns)
    self.er_fama = None  # expected returns of the ff model
    self.ff_betas = None  # ff-betas dict
    self.ff_scores = None  # ff-R^2 of the stocks

    if model == "bl":
      self.prepare_black_litterman(include_ff = False)  # call the prepare bl method
    elif model == "bl-ff":
      self.prepare_black_litterman(include_ff = True)  # prepare bl method with fama-french as views
    elif model == "vanilla-ff":
      self.prepare_ff()

  
  def prepare_ff(self):
    logging.info(f"Computing the expected returns and covar matrix given the FF model")
    # compute log returns
    ln_rt = (np.log(self.historical_prices_df / self.historical_prices_df.shift(1)))[1:]  # log returns
    ln_rt.index = pd.to_datetime(ln_rt.index, format= '%Y%m%d')  # format date

    self.df_stocks_ff = ln_rt.merge(self.ff_factors, left_index = True, right_index = True) # join with the ff factors to expand the dataset

    ff_factors_cols = list(self.ff_factors.columns)  # columns of the FF factors -> Here we could remove/add
    betas={}
    scores={}
    er_fama = pd.DataFrame()
    
    for ticker in self.tickers:
      ff_factors_ticker_cols = ff_factors_cols + [ticker]

      ff_factors_ticker_df = pd.DataFrame()
      ff_factors_ticker_df = copy.deepcopy(self.df_stocks_ff[ff_factors_ticker_cols])
      ff_factors_ticker_df[ticker + "-RF"] = ff_factors_ticker_df[ticker] - ff_factors_ticker_df["RF"]

      # set up the linear regression problem
      x_columns = list(filter(lambda ff_factor: ff_factor != "RF", list(ff_factors_ticker_cols)))  # fama french factors independent vars
      Y = ff_factors_ticker_df.iloc[:,-1]  # dependent var ticker -rf
      X = (ff_factors_ticker_df)[x_columns]  # indep vars (risk factors)

      reg = LinearRegression( fit_intercept = True).fit(X, Y) #regresion
      score = reg.score(X, Y)  # R^2 of the lin reg
      coefs = reg.coef_  # betas
      betas[ticker] = coefs
      scores[ticker] = score
      er_fama[ticker] = np.sum(X * coefs, axis = 1) + ff_factors_ticker_df['RF']  # fama-french expected returns df

    # save the model output
    self.er_fama = er_fama
    self.ff_betas = betas
    self.ff_scores = scores


  def prepare_black_litterman(self, include_ff = False):
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
