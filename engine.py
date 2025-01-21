import pandas as pd
import tqdm as tqdm

class Engine():
    def __init__(self, initial_cash=100_000):
        self.strategy = None
        self.cash = initial_cash
        self.data = None
        self.current_idx = None
        
    def add_data(self, data:pd.DataFrame):
        # Add OHLC data to the engine
        self.data = data
        
    def add_strategy(self, strategy):
        # Add a strategy to the engine
        self.strategy = strategy
    
    def run(self):
        # We need to preprocess a few things before running the backtest
        self.strategy.data = self.data
        
        for idx in tqdm(self.data.index):
            self.current_idx = idx
            self.strategy.current_idx = self.current_idx
            # fill orders from previus period
            self._fill_orders()
            
            # Run the strategy on the current bar
            #self.strategy.on_bar()
            print(idx)
            
    def _fill_orders(self):
        # Fill orders from the previous period
        pass
    
class Strategy():
    """This base class will handle the execution logic of our trading strategies
    """
    def __init__(self):
        pass
    
class Trade():
    """Trade objects are created when an order is filled.
    """
    def __init__(self):
        pass

class Order():
    """When buying or selling, we first create an order object. 
    If the order is filled, we create a trade object.
    """
    def __init__(self):
        pass

import yfinance as yf

data = yf.Ticker('AAPL').history(start='2020-01-01', end='2022-12-31', interval='1d')
e = Engine()
e.add_data(data)
e.add_strategy(Strategy())
e.run()