import yfinance as yf
import logging
import pandas as pd



logging.basicConfig(filename='output.log', filemode='a',
  format='%(asctime)s - %(levelname)-4s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)


class MktDataReader:
  def __init__(self, start_date, end_date, data_source = 'yahoo', tickers = []) -> None:
      self.df_stocks = pd.DataFrame()  # pd.DataFrame that will contain price data for the stocks to analyze 
      self.df_stocks_bkfilled = None
      self.mcaps = None

      self.data_source = data_source
      self.tickers = tickers
      self.start_date = start_date
      self.end_date = end_date

      # call the fetch data method according to the chosen data source
      self.fetch_data()


  def fetch_data(self):
    if self.data_source == "yahoo":
      logging.info(f"Fetching data from yfinance")
      tmp_df = pd.DataFrame(yf.download(self.tickers, start = self.start_date, end = self.end_date))
      fetched_data = tmp_df['Adj Close']  # take the closing price
      self.df_stocks = fetched_data


  def impute_missing_data(self):
    assert self.df_stocks.empty == False, "You haven't fetched the data yet"

    logging.info(f"Imputing missing values with the given strategy bkfill")
    # TODO: add different fill methods
    tmp = self.df_stocks.copy()
    self.df_stocks_bkfilled = tmp.fillna(method='bfill')  # bkfill with the next available price


  def fetch_market_caps(self):
    assert len(self.tickers) != 0, "You need to provide a list of tickers before fetching the mcaps" 
    mcaps = {}
    for t in self.tickers:
      stock = yf.Ticker(t)
      mcaps[t] = stock.info["marketCap"]
    
    self.mcaps = mcaps
