import alpaca_trade_api as tradeapi
import time
from datetime import datetime, timedelta
import logging
import os
import config
from utils.rate_limiter import RATE_LIMITERS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BalanceTracker:
    def __init__(self, api_key, api_secret, base_url):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/v2')
        
        # Create the API client
        self.api = tradeapi.REST(
            key_id=self.api_key,
            secret_key=self.api_secret,
            base_url=self.base_url,
            api_version='v2'
        )
        
        # Initialize tracking variables
        self.previous_balance = None
        self.hour_start_balance = None
        self.hour_start_time = None
        self.day_start_balance = None
        self.day_start_time = None
        
        # Add retry configuration
        self.max_retries = 3
        self.base_delay = 3  # Base delay in seconds
        self.max_delay = 30  # Maximum delay in seconds

    def _make_api_request(self, request_func, *args, **kwargs):
        """Helper method to make API requests with retries and rate limiting"""
        for attempt in range(self.max_retries):
            try:
                # Check rate limit before making request
                if not RATE_LIMITERS['account'].acquire(tokens=1, wait=True):
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    logger.warning(f"Rate limit reached, waiting {delay}s before retry...")
                    time.sleep(delay)
                    continue
                
                return request_func(*args, **kwargs)
                
            except Exception as e:
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                if attempt < self.max_retries - 1:
                    if "too many requests" in str(e).lower():
                        RATE_LIMITERS['account'].record_error()
                        logger.warning(f"Rate limit exceeded. Waiting {delay}s before retry...")
                    elif "subscription does not permit" in str(e).lower():
                        # Skip retrying for subscription-related errors
                        logger.info(f"Skipping retry due to subscription limitation: {str(e)}")
                        break
                    else:
                        logger.warning(f"Request failed: {str(e)}. Retrying in {delay}s... ({attempt + 1}/{self.max_retries})")
                    time.sleep(delay)
                else:
                    logger.error(f"Final attempt failed: {str(e)}")
                    raise
        
        return None  # Return None for failed requests

    def get_account_info(self):
        try:
            # Get account information with retry logic
            account = self._make_api_request(self.api.get_account)
            if not account:
                logger.error("Failed to get account information")
                return None
                
            current_time = datetime.now()
            
            # Get current values
            current_balance = float(account.portfolio_value)
            cash_balance = float(account.cash)
            buying_power = float(account.buying_power)
            
            # Initialize balances if not set
            if self.previous_balance is None:
                self.previous_balance = current_balance
                self.hour_start_balance = current_balance
                self.hour_start_time = current_time
                self.day_start_balance = current_balance
                self.day_start_time = current_time
            
            # Update hourly and daily balances
            if self.hour_start_time is None or (current_time - self.hour_start_time).total_seconds() > 3600:
                self.hour_start_balance = current_balance
                self.hour_start_time = current_time
            
            if self.day_start_time is None or (current_time - self.day_start_time).total_seconds() > 86400:
                self.day_start_balance = current_balance
                self.day_start_time = current_time

            # Calculate changes
            hourly_change = current_balance - self.hour_start_balance
            hourly_change_pct = (hourly_change / self.hour_start_balance) * 100 if self.hour_start_balance else 0
            
            daily_change = current_balance - self.day_start_balance
            daily_change_pct = (daily_change / self.day_start_balance) * 100 if self.day_start_balance else 0
            
            # Update previous balance
            self.previous_balance = current_balance

            # Get positions and orders with retry logic
            positions_data = []
            orders_data = []
            
            try:
                positions = self._make_api_request(self.api.list_positions)
                if positions:
                    positions_data = [{
                        'symbol': pos.symbol,
                        'qty': pos.qty,
                        'side': 'buy' if float(pos.qty) > 0 else 'sell',
                        'avg_entry_price': float(pos.avg_entry_price),
                        'current_price': float(pos.current_price),
                        'unrealized_pl': float(pos.unrealized_pl),
                        'unrealized_plpc': float(pos.unrealized_plpc) * 100
                    } for pos in positions]
            except Exception as e:
                logger.warning(f"Error getting positions: {str(e)}")
                
            try:
                orders = self._make_api_request(lambda: self.api.list_orders(status='open'))
                if orders:
                    orders_data = [{
                        'symbol': order.symbol,
                        'qty': order.qty,
                        'side': order.side,
                        'type': order.type,
                        'limit_price': float(order.limit_price) if order.limit_price else None,
                        'submitted_at': order.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if order.submitted_at else None
                    } for order in orders]
            except Exception as e:
                logger.warning(f"Error getting orders: {str(e)}")

            return {
                'total_equity': current_balance,
                'current_balance': current_balance,
                'cash_balance': cash_balance,
                'buying_power': buying_power,
                'hourly_change': hourly_change,
                'hourly_change_pct': hourly_change_pct,
                'daily_change': daily_change,
                'daily_change_pct': daily_change_pct,
                'positions': positions_data,
                'orders': orders_data,
                'last_update': current_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Error in get_account_info: {str(e)}")
            return None

    def run(self):
        while True:
            info = self.get_account_info()
            if info:
                pass
            time.sleep(10)  # Update every 10 seconds

if __name__ == "__main__":
    # Use config for API credentials
    tracker = BalanceTracker(
        api_key=config.APCA_API_KEY_ID,
        api_secret=config.APCA_API_SECRET_KEY,
        base_url=config.APCA_API_BASE_URL
    )
    
    # Test balance tracking
    while True:
        info = tracker.get_account_info()
        if info:
            print(f"Current balance: ${info['current_balance']:.2f}")
        time.sleep(60)  # Update every minute
