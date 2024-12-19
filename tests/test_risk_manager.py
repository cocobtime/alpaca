import unittest
from unittest.mock import Mock, patch
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk_manager import RiskManager

class TestRiskManager(unittest.TestCase):
    def setUp(self):
        self.risk_manager = RiskManager()

    def test_calculate_position_size(self):
        """Test position size calculation"""
        account_value = 10000.0
        entry_price = 100.0
        risk_per_trade = 0.02  # 2%
        stop_loss_percent = 0.05  # 5%

        position_size = self.risk_manager.calculate_position_size(
            account_value=account_value,
            entry_price=entry_price,
            risk_per_trade=risk_per_trade,
            stop_loss_percent=stop_loss_percent
        )

        # Expected position size calculation:
        # Risk amount = account_value * risk_per_trade = 10000 * 0.02 = 200
        # Risk per share = entry_price * stop_loss_percent = 100 * 0.05 = 5
        # Position size = Risk amount / Risk per share = 200 / 5 = 40
        expected_size = 40
        self.assertEqual(position_size, expected_size)

    def test_check_risk_limits(self):
        """Test risk limits checking"""
        # Test within limits
        current_positions = {
            'AAPL': {'value': 2000},
            'GOOGL': {'value': 3000}
        }
        account_value = 10000.0
        max_position_size = 0.3  # 30%
        max_total_positions = 0.6  # 60%

        result = self.risk_manager.check_risk_limits(
            current_positions=current_positions,
            account_value=account_value,
            max_position_size=max_position_size,
            max_total_positions=max_total_positions
        )

        self.assertTrue(result)

        # Test exceeding limits
        current_positions['MSFT'] = {'value': 4000}
        result = self.risk_manager.check_risk_limits(
            current_positions=current_positions,
            account_value=account_value,
            max_position_size=max_position_size,
            max_total_positions=max_total_positions
        )

        self.assertFalse(result)

    def test_validate_order(self):
        """Test order validation"""
        # Valid order
        order = {
            'symbol': 'AAPL',
            'qty': 10,
            'side': 'buy',
            'type': 'limit',
            'time_in_force': 'day',
            'limit_price': 150.0
        }

        result = self.risk_manager.validate_order(order)
        self.assertTrue(result)

        # Invalid order - missing required fields
        invalid_order = {
            'symbol': 'AAPL',
            'side': 'buy'
        }

        result = self.risk_manager.validate_order(invalid_order)
        self.assertFalse(result)

    def test_calculate_portfolio_risk(self):
        """Test portfolio risk calculation"""
        positions = {
            'AAPL': {'value': 2000, 'unrealized_pl': 200},
            'GOOGL': {'value': 3000, 'unrealized_pl': -100}
        }
        account_value = 10000.0

        risk_metrics = self.risk_manager.calculate_portfolio_risk(
            positions=positions,
            account_value=account_value
        )

        self.assertIsInstance(risk_metrics, dict)
        self.assertIn('total_exposure', risk_metrics)
        self.assertIn('largest_position', risk_metrics)
        self.assertIn('unrealized_pl', risk_metrics)

        # Verify calculations
        self.assertEqual(risk_metrics['total_exposure'], 0.5)  # (2000 + 3000) / 10000
        self.assertEqual(risk_metrics['largest_position'], 0.3)  # 3000 / 10000
        self.assertEqual(risk_metrics['unrealized_pl'], 100)  # 200 + (-100)

if __name__ == '__main__':
    unittest.main()
