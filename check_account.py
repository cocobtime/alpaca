import alpaca_trade_api as tradeapi
import logging
import os

logging.basicConfig(level=logging.INFO)

API_KEY = os.environ.get("ALPACA_API_KEY")
API_SECRET = os.environ.get("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

try:
    api = tradeapi.REST(API_KEY, API_SECRET, base_url=BASE_URL, api_version='v2')
    account = api.get_account()
    print("\n=== Account Information ===")
    print(f"Account Status: {account.status}")
    print(f"Cash: ${float(account.cash):,.2f}")
    print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"Buying Power: ${float(account.buying_power):,.2f}")
    print(f"Initial Margin: ${float(account.initial_margin):,.2f}")
    print(f"Last Equity: ${float(account.last_equity):,.2f}")
    print(f"Multiplier: {account.multiplier}")
    print("=========================\n")
except Exception as e:
    print(f"Error accessing account: {e}")
