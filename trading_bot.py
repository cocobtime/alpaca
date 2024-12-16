import alpaca_trade_api as tradeapi
import numpy as np
import time
from collections import defaultdict
import random
import logging
from datetime import datetime
import socketio
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TradingBot:
    def __init__(self, api_key, api_secret, base_url, socketio=None):
        self.api = tradeapi.REST(
            key_id=api_key,
            secret_key=api_secret,
            base_url=base_url,
            api_version='v2'
        )
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.3  # For exploration
        self.position_size = 100  # Number of shares to trade
        self.min_price_change = 0.001  # Minimum price change to consider
        self.last_prices = {}
        self.positions = {}
        self.socketio = socketio
        
    def get_state(self, symbol, current_price):
        """Generate state based on current market conditions"""
        position = self.positions.get(symbol, 0)
        last_price = self.last_prices.get(symbol, current_price)
        price_change = (current_price - last_price) / last_price if last_price else 0
        
        # Discretize the state
        if position > 0:
            position_state = "long"
        elif position < 0:
            position_state = "short"
        else:
            position_state = "neutral"
            
        if abs(price_change) < self.min_price_change:
            price_state = "stable"
        elif price_change > 0:
            price_state = "up"
        else:
            price_state = "down"
            
        return f"{position_state}_{price_state}"
    
    def get_action(self, state):
        """Choose action using epsilon-greedy policy"""
        if random.random() < self.epsilon:
            return random.choice(["buy", "sell", "hold"])
        
        q_values = self.q_table[state]
        if not q_values:  # If no Q-values exist for this state
            return random.choice(["buy", "sell", "hold"])
        
        return max(q_values.items(), key=lambda x: x[1])[0]
    
    def calculate_reward(self, symbol, action, price_before, price_after):
        """Calculate reward based on action and price change"""
        if action == "hold":
            return 0
        
        price_change = (price_after - price_before) / price_before
        position = self.positions.get(symbol, 0)
        
        if action == "buy":
            return price_change * 100  # Positive if price went up
        elif action == "sell":
            return -price_change * 100  # Positive if price went down
            
        return 0
    
    def execute_trade(self, symbol, action):
        """Execute trade on Alpaca"""
        try:
            if action == "hold":
                return
            
            side = "buy" if action == "buy" else "sell"
            qty = self.position_size
            
            # Submit order
            self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='market',
                time_in_force='gtc'
            )
            
            # Update positions
            position_change = qty if side == "buy" else -qty
            self.positions[symbol] = self.positions.get(symbol, 0) + position_change
            
            # Emit trade update
            if self.socketio:
                self.socketio.emit('trade_update', {
                    'symbol': symbol,
                    'action': action,
                    'price': float(self.last_prices.get(symbol, 0)),
                    'quantity': qty,
                    'timestamp': datetime.now().isoformat()
                })
            
            logging.info(f"Executed {side} order for {qty} shares of {symbol}")
            
        except Exception as e:
            logging.error(f"Error executing trade: {e}")
    
    def update_q_table(self, state, action, reward, next_state):
        """Update Q-table using Q-learning algorithm"""
        old_value = self.q_table[state][action]
        next_max = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0
        
        new_value = (1 - self.learning_rate) * old_value + \
                   self.learning_rate * (reward + self.discount_factor * next_max)
        
        self.q_table[state][action] = new_value
    
    def run(self, symbols):
        """Main trading loop"""
        logging.info("Starting trading bot...")
        
        while True:
            try:
                portfolio_positions = {}
                for symbol in symbols:
                    # Get current price
                    try:
                        quote = self.api.get_latest_trade(symbol)
                        current_price = float(quote.price)
                    except Exception as e:
                        logging.error(f"Error getting price for {symbol}: {e}")
                        continue
                    
                    # Get current state
                    state = self.get_state(symbol, current_price)
                    
                    # Choose and execute action
                    action = self.get_action(state)
                    price_before = current_price
                    
                    self.execute_trade(symbol, action)
                    
                    # Wait for a short time to let the trade execute
                    time.sleep(1)
                    
                    # Get new price and calculate reward
                    try:
                        quote = self.api.get_latest_trade(symbol)
                        price_after = float(quote.price)
                    except Exception as e:
                        logging.error(f"Error getting price after trade: {e}")
                        continue
                    
                    reward = self.calculate_reward(symbol, action, price_before, price_after)
                    
                    # Get new state and update Q-table
                    next_state = self.get_state(symbol, price_after)
                    self.update_q_table(state, action, reward, next_state)
                    
                    # Update last price
                    self.last_prices[symbol] = price_after
                    
                    # Log the action and result
                    logging.info(f"Symbol: {symbol}, State: {state}, Action: {action}, Reward: {reward:.4f}")
                    
                    # Get position information
                    try:
                        position = self.api.get_position(symbol)
                        portfolio_positions[symbol] = {
                            'qty': position.qty,
                            'market_value': position.market_value,
                            'unrealized_pl': position.unrealized_plpc
                        }
                    except:
                        pass
                
                # Emit portfolio update
                if self.socketio:
                    self.socketio.emit('portfolio_update', {
                        'positions': portfolio_positions,
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Small delay between iterations
                time.sleep(5)
                
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(5)

if __name__ == "__main__":
    # Configuration
    API_KEY = os.environ.get("ALPACA_API_KEY")
    API_SECRET = os.environ.get("ALPACA_SECRET_KEY")
    BASE_URL = "https://paper-api.alpaca.markets"
    
    # Get list of tradable symbols
    api = tradeapi.REST()
    assets = api.list_assets()
    tradable_symbols = [asset.symbol for asset in assets if asset.tradable]
    
    # Take the first 10 tradable symbols
    trading_symbols = tradable_symbols[:10]
    logging.info(f"Trading symbols: {trading_symbols}")
    
    # Create and run the trading bot
    bot = TradingBot(API_KEY, API_SECRET, BASE_URL)
    bot.run(trading_symbols)
