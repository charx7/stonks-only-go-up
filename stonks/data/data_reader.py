import yfinance as yf
import logging
import pandas as pd
import zipfile
import urllib.request

logging.basicConfig(filename='output.log', filemode='a',
  format='%(asctime)s - %(levelname)-4s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)


class MktDataReader:
  def __init__(self, start_date, end_date, data_source = 'yahoo', tickers = []) -> None:
      self.df_stocks = pd.DataFrame()  # pd.DataFrame that will contain price data for the stocks to analyze 
      self.df_stocks_bkfilled = None
      self.mcaps = None  # market caps
      self.ff_factors = None  # fama-french factors

      self.data_source = data_source
      self.tickers = tickers
      self.start_date = start_date
      self.end_date = end_date

      # call the fetch data method according to the chosen data source
      self.fetch_data()

      # call the fetch method for the fama french factors df
      self.fetch_fama_french()


  def fetch_fama_french(self, period = "daily"):
    if period == "daily":
      ff_url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
    elif period == "monthly":
      ff_url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_CSV.zip"

    # Download the file and save it
    # We will name it fama_french.zip file
    urllib.request.urlretrieve(ff_url,'fama_french.zip')
    zip_file = zipfile.ZipFile('fama_french.zip', 'r')
    
    # Next we extact the file data   
    zip_file.extractall()
    
    # Make sure you close the file after extraction 
    zip_file.close()
    
    # Now open the CSV file    
    ff_factors = pd.read_csv('F-F_Research_Data_5_Factors_2x3_daily.CSV', skiprows = 3, index_col = 0)

    # Format the date index
    ff_factors.index = pd.to_datetime(ff_factors.index, format= '%Y%m%d')
    
    # set the famma french factors in the MktDataReader class
    self.ff_factors = pd.DataFrame(ff_factors)


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
