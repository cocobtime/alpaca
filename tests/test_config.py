import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *

class TestConfiguration(unittest.TestCase):
    def setUp(self):
        # Save original environment variables
        self.original_env = {}
        for key in ['APCA_API_KEY_ID', 'APCA_API_SECRET_KEY', 'APCA_API_BASE_URL']:
            self.original_env[key] = os.environ.get(key)

    def tearDown(self):
        # Restore original environment variables
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_api_credentials(self):
        """Test API credentials configuration"""
        # Test with environment variables
        test_key = 'test_api_key'
        test_secret = 'test_secret_key'
        test_url = 'https://paper-api.alpaca.markets'

        os.environ['APCA_API_KEY_ID'] = test_key
        os.environ['APCA_API_SECRET_KEY'] = test_secret
        os.environ['APCA_API_BASE_URL'] = test_url

        self.assertEqual(APCA_API_KEY_ID, test_key)
        self.assertEqual(APCA_API_SECRET_KEY, test_secret)
        self.assertEqual(APCA_API_BASE_URL, test_url)

    def test_trading_parameters(self):
        """Test trading parameters configuration"""
        # Test risk parameters
        self.assertIsInstance(MAX_POSITION_SIZE, float)
        self.assertGreater(MAX_POSITION_SIZE, 0)
        self.assertLess(MAX_POSITION_SIZE, 1)

        # Test strategy parameters
        self.assertIsInstance(SYMBOLS, list)
        self.assertTrue(all(isinstance(s, str) for s in SYMBOLS))

        # Test timeframes
        self.assertIsInstance(TIMEFRAMES, dict)
        for key, value in TIMEFRAMES.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, int)

    def test_api_endpoints(self):
        """Test API endpoints configuration"""
        # Test that base URL is valid
        self.assertTrue(
            APCA_API_BASE_URL.startswith('http://') or 
            APCA_API_BASE_URL.startswith('https://')
        )

    def test_logging_configuration(self):
        """Test logging configuration"""
        self.assertIsInstance(LOG_LEVEL, str)
        self.assertIn(LOG_LEVEL, ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])

    def test_database_configuration(self):
        """Test database configuration"""
        self.assertIsInstance(DB_PATH, str)
        self.assertTrue(DB_PATH.endswith('.db'))

if __name__ == '__main__':
    unittest.main()
