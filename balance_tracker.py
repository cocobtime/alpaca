import alpaca_trade_api as tradeapi
import time
from datetime import datetime, timedelta
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BalanceTracker:
    def __init__(self, api_key, api_secret, base_url):
        # Store the credentials
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        
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

    def get_account_info(self):
        try:
            account = self.api.get_account()
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
            
            # Update hourly balance if needed
            if self.hour_start_time is None or (current_time - self.hour_start_time).total_seconds() > 3600:
                self.hour_start_balance = current_balance
                self.hour_start_time = current_time
            
            # Update daily balance if needed
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

            return {
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_equity': current_balance,
                'cash_balance': cash_balance,
                'buying_power': buying_power,
                'hourly_change': hourly_change,
                'hourly_change_pct': hourly_change_pct,
                'daily_change': daily_change,
                'daily_change_pct': daily_change_pct,
                'account_status': account.status
            }
        except Exception as e:
            logging.error(f"Error getting account info: {e}")
            return None

    def run(self):
        while True:
            info = self.get_account_info()
            if info:
                pass
            time.sleep(10)  # Update every 10 seconds
if __name__ == "__main__":
    API_KEY = os.environ.get("ALPACA_API_KEY")
    API_SECRET = os.environ.get("ALPACA_SECRET_KEY")
    BASE_URL = "https://paper-api.alpaca.markets"
    
    tracker = BalanceTracker(API_KEY, API_SECRET, BASE_URL)
    tracker.run()
