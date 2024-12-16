from balance_tracker import BalanceTracker
import json

def test_balance():
    # Configuration
    API_KEY = "PKY2G5O6O2XDO493SU2X"
    API_SECRET = "vm3aV23EKDCZA7EKUTmKPvpsVc1hdhf52yNXLDrv"
    BASE_URL = "https://paper-api.alpaca.markets"
    
    # Create balance tracker instance
    tracker = BalanceTracker(API_KEY, API_SECRET, BASE_URL)
    
    # Get account info
    info = tracker.get_account_info()
    
    # Print the results
    print("\n=== Account Information ===")
    print(json.dumps(info, indent=2))
    print("=========================\n")
    
    return info

if __name__ == "__main__":
    test_balance()
