import unittest
from unittest.mock import Mock, patch
import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indicators import TechnicalIndicators

class TestTechnicalIndicators(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        # Create sample price data
        self.test_data = pd.DataFrame({
            'close': np.random.randn(100).cumsum() + 100,
            'high': np.random.randn(100).cumsum() + 102,
            'low': np.random.randn(100).cumsum() + 98,
            'volume': np.random.randint(1000, 10000, 100)
        })
        self.indicators = TechnicalIndicators()

    def test_calculate_sma(self):
        """Test Simple Moving Average calculation"""
        period = 20
        sma = self.indicators.calculate_sma(self.test_data['close'], period)
        
        # Verify shape and NaN values
        self.assertEqual(len(sma), len(self.test_data))
        self.assertEqual(sum(sma.isna()), period - 1)
        
        # Verify calculation
        manual_sma = self.test_data['close'].rolling(window=period).mean()
        pd.testing.assert_series_equal(sma, manual_sma, check_names=False)

    def test_calculate_ema(self):
        """Test Exponential Moving Average calculation"""
        period = 20
        ema = self.indicators.calculate_ema(self.test_data['close'], period)
        
        # Verify shape and NaN values
        self.assertEqual(len(ema), len(self.test_data))
        self.assertEqual(sum(ema.isna()), period - 1)

    def test_calculate_rsi(self):
        """Test Relative Strength Index calculation"""
        period = 14
        rsi = self.indicators.calculate_rsi(self.test_data['close'], period)
        
        # Verify shape and value range
        self.assertEqual(len(rsi), len(self.test_data))
        self.assertTrue(all((0 <= x <= 100) for x in rsi.dropna()))

    def test_calculate_macd(self):
        """Test MACD calculation"""
        macd, signal, hist = self.indicators.calculate_macd(
            self.test_data['close'],
            fast_period=12,
            slow_period=26,
            signal_period=9
        )
        
        # Verify shapes
        self.assertEqual(len(macd), len(self.test_data))
        self.assertEqual(len(signal), len(self.test_data))
        self.assertEqual(len(hist), len(self.test_data))

    def test_calculate_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        period = 20
        upper, middle, lower = self.indicators.calculate_bollinger_bands(
            self.test_data['close'],
            period=period,
            num_std=2
        )
        
        # Verify shapes
        self.assertEqual(len(upper), len(self.test_data))
        self.assertEqual(len(middle), len(self.test_data))
        self.assertEqual(len(lower), len(self.test_data))
        
        # Verify band relationships
        self.assertTrue(all(upper.dropna() >= middle.dropna()))
        self.assertTrue(all(middle.dropna() >= lower.dropna()))

    def test_calculate_atr(self):
        """Test Average True Range calculation"""
        period = 14
        atr = self.indicators.calculate_atr(
            self.test_data['high'],
            self.test_data['low'],
            self.test_data['close'],
            period
        )
        
        # Verify shape and values
        self.assertEqual(len(atr), len(self.test_data))
        self.assertTrue(all(x >= 0 for x in atr.dropna()))

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test with empty data
        empty_data = pd.Series([])
        with self.assertRaises(ValueError):
            self.indicators.calculate_sma(empty_data, 20)

        # Test with invalid period
        with self.assertRaises(ValueError):
            self.indicators.calculate_sma(self.test_data['close'], 0)

        # Test with period longer than data
        with self.assertRaises(ValueError):
            self.indicators.calculate_sma(self.test_data['close'], len(self.test_data) + 1)

if __name__ == '__main__':
    unittest.main()
