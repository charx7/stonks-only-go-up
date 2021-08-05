from stonks.data.data_reader import MktDataReader


class AssetAllocation:
  def __init__(self, mkt_data_reader: MktDataReader, allocation_stategy: str) -> None:
      # class properties
      self.mkt_data_reader = mkt_data_reader
      self.strategy = allocation_stategy
      