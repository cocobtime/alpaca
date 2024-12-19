import requests

def check_balance():
    api_key = 'PK4J8DOVMNQT9P4GYV6A'
    api_secret = '9NtS5BccK4JlMaTbMYpoEqaxpGkMd5exFJZ75Nj7'
    base_url = 'https://paper-api.alpaca.markets/v2'

    headers = {
        'APCA-API-KEY-ID': api_key,
        'APCA-API-SECRET-KEY': api_secret
    }

    try:
        # Get account information
        account_response = requests.get(f'{base_url}/account', headers=headers)
        account_data = account_response.json()

        print("Alpaca Paper Trading Account Details:")
        print(f"Total Account Value: ${account_data.get('equity', 'N/A')}")
        print(f"Buying Power: ${account_data.get('buying_power', 'N/A')}")
        print(f"Cash: ${account_data.get('cash', 'N/A')}")
        
        # Get positions
        positions_response = requests.get(f'{base_url}/positions', headers=headers)
        positions_data = positions_response.json()
        
        print("\nCurrent Positions:")
        if positions_data:
            for position in positions_data:
                print(f"{position.get('symbol', 'Unknown')}: {position.get('qty', 'N/A')} shares")
        else:
            print("No current positions")

    except Exception as e:
        print(f"Error accessing account: {e}")

if __name__ == "__main__":
    check_balance()
