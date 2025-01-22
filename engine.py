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
        for order in self.strategy.orders:
            can_fill = False
            if order.side == 'buy' and self.cash >= self.data.loc[self.current_idx]['Open'] * order.size:
                can_fill = True 
            elif order.side == 'sell' and self.strategy.position_size >= order.size:
                can_fill = True
            if can_fill:
                t = Trade(
                    ticker = order.ticker,
                    side = order.side,
                    price= self.data.loc[self.current_idx]['Open'],
                    size = order.size,
                    type = order.type,
                    idx = self.current_idx)

                self.strategy.trades.append(t)
                self.cash -= t.price * t.size
        self.strategy.orders = []
    
class Strategy():
    """This base class will handle the execution logic of our trading strategies
    """
    def __init__(self):
        self.current_idx = None
        self.data = None
        self.orders = []
        self.trades = []
    
    def buy(self,ticker,size=1):
        self.orders.append(
            Order(
                ticker = ticker,
                side = 'buy',
                size = size,
                idx = self.current_idx
            ))

    def sell(self,ticker,size=1):
        self.orders.append(
            Order(
                ticker = ticker,
                side = 'sell',
                size = -size,
                idx = self.current_idx
            ))
        
    @property
    def position_size(self):
        return sum([t.size for t in self.trades])
        
    def on_bar(self):
        """This method will be overriden by our strategies.
        """
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
    def __init__(self, ticker, size, side, idx):
        self.ticker = ticker
        self.side = side
        self.size = size
        self.type = 'market'
        self.idx = idx
        
class Trade():
    def __init__(self, ticker,side,size,price,type,idx):
        self.ticker = ticker
        self.side = side
        self.price = price
        self.size = size
        self.type = type
        self.idx = idx

import yfinance as yf

class BuyAndSellSwitch(Strategy):
    def on_bar(self):
        if self.position_size == 0:
            self.buy('AAPL', 1)
            print(self.current_idx,"buy")
        else:
            self.sell('AAPL', 1)
            print(self.current_idx,"sell")

data = yf.Ticker('AAPL').history(start='2022-12-01', end='2022-12-31', interval='1d')
e = Engine()
e.add_data(data)
e.add_strategy(BuyAndSellSwitch())
e.run()            