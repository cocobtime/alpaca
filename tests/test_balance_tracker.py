import unittest
from unittest.mock import Mock, patch
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from balance_tracker import BalanceTracker

class TestBalanceTracker(unittest.TestCase):
    def setUp(self):
        self.api_key = 'test_key'
        self.api_secret = 'test_secret'
        self.base_url = 'https://paper-api.alpaca.markets'
        self.tracker = BalanceTracker(self.api_key, self.api_secret, self.base_url)

    def test_initialization(self):
        """Test if balance tracker initializes correctly"""
        self.assertEqual(self.tracker.api_key, self.api_key)
        self.assertEqual(self.tracker.api_secret, self.api_secret)
        self.assertEqual(self.tracker.base_url, self.base_url)
        self.assertIsNone(self.tracker.previous_balance)
        self.assertIsNone(self.tracker.hour_start_balance)
        self.assertIsNone(self.tracker.day_start_balance)

    @patch('alpaca_trade_api.REST')
    def test_get_account_info(self, mock_api):
        """Test getting account information"""
        # Mock account response
        mock_account = Mock()
        mock_account.portfolio_value = '10000.00'
        mock_account.cash = '5000.00'
        mock_account.buying_power = '5000.00'
        
        # Mock positions
        mock_position = Mock()
        mock_position.symbol = 'AAPL'
        mock_position.qty = '10'
        mock_position.avg_entry_price = '150.00'
        mock_position.current_price = '160.00'
        mock_position.unrealized_pl = '100.00'
        mock_position.unrealized_plpc = '0.0667'
        
        # Mock orders
        mock_order = Mock()
        mock_order.symbol = 'GOOGL'
        mock_order.qty = '5'
        mock_order.side = 'buy'
        mock_order.type = 'limit'
        mock_order.limit_price = '2500.00'
        mock_order.submitted_at = datetime.now()
        
        # Configure mock API
        mock_api.return_value.get_account.return_value = mock_account
        mock_api.return_value.list_positions.return_value = [mock_position]
        mock_api.return_value.list_orders.return_value = [mock_order]
        
        # Get account info
        info = self.tracker.get_account_info()
        
        # Verify the response
        self.assertIsNotNone(info)
        self.assertEqual(float(info['total_equity']), 10000.00)
        self.assertEqual(float(info['cash_balance']), 5000.00)
        self.assertEqual(float(info['buying_power']), 5000.00)
        
        # Verify positions data
        self.assertEqual(len(info['positions']), 1)
        position = info['positions'][0]
        self.assertEqual(position['symbol'], 'AAPL')
        self.assertEqual(position['qty'], '10')
        
        # Verify orders data
        self.assertEqual(len(info['orders']), 1)
        order = info['orders'][0]
        self.assertEqual(order['symbol'], 'GOOGL')
        self.assertEqual(order['qty'], '5')

    def test_api_error_handling(self):
        """Test API error handling"""
        with patch('alpaca_trade_api.REST') as mock_api:
            # Simulate API error
            mock_api.return_value.get_account.side_effect = Exception('API Error')
            
            # Verify error handling
            info = self.tracker.get_account_info()
            self.assertIsNone(info)

    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        with patch('time.sleep') as mock_sleep:
            with patch('alpaca_trade_api.REST') as mock_api:
                # Simulate rate limit error
                mock_api.return_value.get_account.side_effect = [
                    Exception('too many requests'),
                    Mock(portfolio_value='10000.00', cash='5000.00', buying_power='5000.00')
                ]
                
                # Get account info
                info = self.tracker.get_account_info()
                
                # Verify rate limiting behavior
                mock_sleep.assert_called()
                self.assertIsNotNone(info)

if __name__ == '__main__':
    unittest.main()
