import pandas as pd
from tqdm import tqdm


class Order():
    def __init__(self, ticker, size, side, idx, limit_price=None, order_type='market'):
        self.ticker = ticker
        self.side = side
        self.size = size
        self.type = 'market'
        self.idx = idx
        self.type = order_type
        self.limit_price = limit_price
        
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
    @property
    def close(self):
        return self.data.loc[self.current_idx]['Close']

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
        
    def buy_limit(self,ticker,limit_price, size=1):
        self.orders.append(
            Order(
                ticker = ticker,
                side = 'buy',
                size = size,
                limit_price=limit_price,
                order_type='limit',
                idx = self.current_idx
            ))

    def sell_limit(self,ticker,limit_price, size=1):
        self.orders.append(
            Order(
                ticker = ticker,
                side = 'sell',
                size = -size,
                limit_price=limit_price,
                order_type='limit',
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
        for order in self.strategy.orders:
            # FOR NOW, SET FILL PRICE TO EQUAL OPEN PRICE. THIS HOLDS TRUE FOR MARKET ORDERS
            fill_price = self.data.loc[self.current_idx]['Open']
            can_fill = False
            if order.side == 'buy' and self.cash >= self.data.loc[self.current_idx]['Open'] * order.size:
                if order.type == 'limit':
                    # LIMIT BUY ORDERS ONLY GET FILLED IF THE LIMIT PRICE IS GREATER THAN OR EQUAL TO THE LOW PRICE
                    if order.limit_price >= self.data.loc[self.current_idx]['Low']:
                        ill_price = order.limit_price
                        can_fill = True
                        print(self.current_idx, 'Buy Filled. ', "limit",order.limit_price," / low", self.data.loc[self.current_idx]['Low'])

                    else:
                        print(self.current_idx,'Buy NOT filled. ', "limit",order.limit_price," / low", self.data.loc[self.current_idx]['Low'])
                else:        
                    can_fill = True 
            elif order.side == 'sell' and self.strategy.position_size >= order.size:
                if order.type == 'limit':
                    #LIMIT SELL ORDERS ONLY GET FILLED IF THE LIMIT PRICE IS LESS THAN OR EQUAL TO THE HIGH PRICE
                    if order.limit_price <= self.data.loc[self.current_idx]['High']:
                        fill_price = order.limit_price
                        can_fill = True
                        print(self.current_idx,'Sell filled. ', "limit",order.limit_price," / high", self.data.loc[self.current_idx]['High'])

                    else:
                        print(self.current_idx,'Sell NOT filled. ', "limit",order.limit_price," / high", self.data.loc[self.current_idx]['High'])
                else:
                    can_fill = True
                
        if can_fill:
            t = Trade(
                ticker = order.ticker,
                side = order.side,
                price= fill_price,
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