import unittest
from unittest.mock import Mock, patch
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading_bot import MockTradingBot

class TestMockTradingBot(unittest.TestCase):
    def setUp(self):
        # Set up environment variables for testing
        os.environ['ALPACA_API_KEY'] = 'test_key'
        os.environ['ALPACA_SECRET_KEY'] = 'test_secret'
        self.bot = MockTradingBot()

    def test_initialization(self):
        """Test if bot initializes correctly"""
        self.assertEqual(self.bot.api_key, 'test_key')
        self.assertEqual(self.bot.api_secret, 'test_secret')
        self.assertIsNotNone(self.bot.account)
        self.assertIsInstance(self.bot.symbols, list)

    def test_simulate_market_prices(self):
        """Test market price simulation"""
        prices = self.bot.simulate_market_prices()
        self.assertIsInstance(prices, dict)
        for symbol in self.bot.symbols:
            self.assertIn(symbol, prices)
            self.assertIsInstance(prices[symbol], float)
            self.assertGreater(prices[symbol], 0)

    def test_simulate_trading(self):
        """Test trading simulation"""
        initial_balance = self.bot.account['total_equity']
        initial_buying_power = self.bot.account['buying_power']
        
        self.bot.simulate_trading()
        
        # Check that balances have changed
        self.assertNotEqual(self.bot.account['total_equity'], initial_balance)
        self.assertNotEqual(self.bot.account['buying_power'], initial_buying_power)
        
        # Check that we haven't spent more than our buying power
        self.assertGreaterEqual(self.bot.account['buying_power'], 0)

    def test_missing_api_keys(self):
        """Test handling of missing API keys"""
        # Remove environment variables
        if 'ALPACA_API_KEY' in os.environ:
            del os.environ['ALPACA_API_KEY']
        if 'ALPACA_SECRET_KEY' in os.environ:
            del os.environ['ALPACA_SECRET_KEY']
            
        with self.assertRaises(SystemExit):
            MockTradingBot()

    def test_run_method(self):
        """Test the main run method"""
        with patch('builtins.print') as mock_print:
            self.bot.run()
            mock_print.assert_called()

if __name__ == '__main__':
    unittest.main()
