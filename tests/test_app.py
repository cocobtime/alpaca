import unittest
from unittest.mock import Mock, patch
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, get_market_status

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Set up environment variables
        os.environ['APCA_API_KEY_ID'] = 'test_key'
        os.environ['APCA_API_SECRET_KEY'] = 'test_secret'

    def test_index_route(self):
        """Test the main index route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    @patch('alpaca_trade_api.REST')
    def test_market_status_regular(self, mock_api):
        """Test market status detection for regular hours"""
        # Mock clock response for regular hours
        mock_clock = Mock()
        mock_clock.is_open = True
        mock_clock.next_close = datetime.now() + timedelta(hours=4)
        mock_clock.next_open = datetime.now() - timedelta(hours=2)
        
        mock_api.return_value.get_clock.return_value = mock_clock
        
        status = get_market_status(mock_api.return_value)
        self.assertEqual(status, 'REGULAR')

    @patch('alpaca_trade_api.REST')
    def test_market_status_extended(self, mock_api):
        """Test market status detection for extended hours"""
        # Mock clock response for extended hours
        mock_clock = Mock()
        mock_clock.is_open = True
        mock_clock.next_close = datetime.now() + timedelta(hours=1)
        mock_clock.next_open = datetime.now() + timedelta(hours=2)
        
        mock_api.return_value.get_clock.return_value = mock_clock
        
        status = get_market_status(mock_api.return_value)
        self.assertEqual(status, 'EXTENDED')

    @patch('alpaca_trade_api.REST')
    def test_market_status_closed(self, mock_api):
        """Test market status detection for closed market"""
        # Mock clock response for closed market
        mock_clock = Mock()
        mock_clock.is_open = False
        
        mock_api.return_value.get_clock.return_value = mock_clock
        
        status = get_market_status(mock_api.return_value)
        self.assertEqual(status, 'CLOSED')

    @patch('alpaca_trade_api.REST')
    def test_market_status_error(self, mock_api):
        """Test market status error handling"""
        # Simulate API error
        mock_api.return_value.get_clock.side_effect = Exception('API Error')
        
        status = get_market_status(mock_api.return_value)
        self.assertEqual(status, 'UNKNOWN')

if __name__ == '__main__':
    unittest.main()
