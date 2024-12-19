import pytest
import os
import sys
from unittest.mock import Mock
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_alpaca_api():
    """Fixture for mocked Alpaca API"""
    mock_api = Mock()
    
    # Mock account
    mock_account = Mock(
        portfolio_value='10000.00',
        cash='5000.00',
        buying_power='5000.00'
    )
    
    # Mock position
    mock_position = Mock(
        symbol='AAPL',
        qty='10',
        avg_entry_price='150.00',
        current_price='160.00',
        unrealized_pl='100.00',
        unrealized_plpc='0.0667'
    )
    
    # Mock order
    mock_order = Mock(
        symbol='AAPL',
        qty='10',
        side='buy',
        type='market',
        submitted_at=datetime.now()
    )
    
    # Configure mock API methods
    mock_api.get_account.return_value = mock_account
    mock_api.list_positions.return_value = [mock_position]
    mock_api.list_orders.return_value = [mock_order]
    
    return mock_api

@pytest.fixture
def test_env_vars():
    """Fixture for test environment variables"""
    # Save original environment variables
    original_env = {}
    test_vars = {
        'APCA_API_KEY_ID': 'test_key',
        'APCA_API_SECRET_KEY': 'test_secret',
        'APCA_API_BASE_URL': 'https://paper-api.alpaca.markets'
    }
    
    # Save and set environment variables
    for key in test_vars:
        original_env[key] = os.environ.get(key)
        os.environ[key] = test_vars[key]
    
    yield test_vars
    
    # Restore original environment variables
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

@pytest.fixture
def sample_market_data():
    """Fixture for sample market data"""
    return {
        'AAPL': {
            'close': [150.0, 151.0, 152.0, 151.5, 153.0],
            'high': [152.0, 153.0, 154.0, 153.5, 155.0],
            'low': [149.0, 150.0, 151.0, 150.5, 152.0],
            'volume': [1000000, 1100000, 950000, 1050000, 1200000]
        }
    }

@pytest.fixture
def sample_order():
    """Fixture for sample order data"""
    return {
        'symbol': 'AAPL',
        'qty': 10,
        'side': 'buy',
        'type': 'limit',
        'time_in_force': 'day',
        'limit_price': 150.0
    }
