import numpy as np
import logging
from config import Config

class RiskManager:
    def __init__(self, api_client):
        self.api = api_client
        self.portfolio_risk = 0.0
    
    def calculate_portfolio_correlation(self, symbols):
        """Calculate correlation between trading symbols"""
        try:
            # Fetch historical data for symbols
            historical_data = {}
            for symbol in symbols:
                bars = self.api.get_bars(
                    symbol, 
                    '1D', 
                    limit=30
                ).df['close']
                historical_data[symbol] = bars
            
            # Calculate correlation matrix
            correlation_matrix = np.corrcoef(list(historical_data.values()))
            max_correlation = np.max(np.abs(correlation_matrix[np.triu_indices(len(symbols), k=1)]))
            
            return max_correlation < Config.CORRELATION_THRESHOLD
        
        except Exception as e:
            logging.error(f"Correlation calculation error: {e}")
            return False
    
    def is_safe_to_trade(self, symbol):
        """Check if it's safe to trade a symbol"""
        try:
            # Check portfolio risk
            account = self.api.get_account()
            current_risk = float(account.non_marginable_buying_power) / float(account.equity)
            
            if current_risk > Config.MAX_TOTAL_RISK_PERCENT:
                logging.warning(f"Portfolio risk too high: {current_risk * 100}%")
                return False
            
            # Check individual symbol risk
            return self._check_symbol_health(symbol)
        
        except Exception as e:
            logging.error(f"Risk check error: {e}")
            return False
    
    def _check_symbol_health(self, symbol):
        """Perform detailed health check on a symbol"""
        try:
            # Get last trade price and volume
            last_trade = self.api.get_last_trade(symbol)
            asset = self.api.get_asset(symbol)
            
            # Basic health checks
            checks = [
                last_trade.price > 5.0,  # Minimum price
                last_trade.price < 500.0,  # Maximum price
                asset.easy_to_borrow,
                asset.tradable,
                asset.marginable
            ]
            
            return all(checks)
        
        except Exception as e:
            logging.error(f"Symbol health check error for {symbol}: {e}")
            return False
