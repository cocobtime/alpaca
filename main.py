import alpaca_trade_api as tradeapi
import os
from alpaca_trade_api.rest import APIError

def verify_api_keys(api_key, secret_key):
    """
    Verifies the Alpaca API keys by attempting to fetch account information.

    Returns:
        bool: True if the keys are valid, False otherwise.
    """
    try:
        api = tradeapi.REST(api_key, secret_key, base_url='https://paper-api.alpaca.markets', api_version='v2')
        api.get_account()
        return True
    except APIError as e:
        print(f"Error verifying API keys: {e}")
        return False

def get_account_balance():
    """
    Fetches the account balance from Alpaca's trading API.

    Returns:
        float: The account balance, or None if an error occurred.
    """
    api_key = os.environ.get("ALPACA_API_KEY")
    secret_key = os.environ.get("ALPACA_SECRET_KEY")

    if not api_key or not secret_key:
        print("Error: ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables must be set.")
        return None

    # Basic validation of API key format
    if not (api_key.startswith("PK") and len(api_key) == 20):
        print("Error: Invalid ALPACA_API_KEY format.")
        return None

    try:
        api = tradeapi.REST(api_key, secret_key, base_url='https://paper-api.alpaca.markets', api_version='v2')
        account = api.get_account()
        if account.status != 'ACTIVE':
            print(f"Error: Account is not active. Status: {account.status}")
            return None
        return account.cash
    except APIError as e:
        print(f"Error fetching account balance: {e}")
        return None
