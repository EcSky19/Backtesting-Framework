import pandas as pd
from tqdm import tqdm


class Order():
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
    def __repr__(self):
        return f'<Trade: {self.idx} {self.ticker} {self.size}@{self.price}>'

class Strategy():
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

class Engine():
    def __init__(self, initial_cash=100_000):
        self.strategy = None
        self.cash = initial_cash
        self.initial_cash = initial_cash
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
            self.strategy.on_bar()
        return self._get_stats()
                
    def _fill_orders(self):
        """this method fills buy and sell orders, creating new trade objects and adjusting the strategy's cash balance.
        Conditions for filling an order:
        - If we're buying, our cash balance has to be large enough to cover the order.
        - If we are selling, we have to have enough shares to cover the order.
        """
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
    
    def _get_stats(self):
        metrics = {}
        total_return = 100 *((self.data.loc[self.current_idx]['Close'] * self.strategy.position_size + self.cash) / self.initial_cash -1)
        metrics['total_return'] = total_return
        return metrics#