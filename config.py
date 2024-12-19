import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # Alpaca Trading Configuration
    ALPACA_API_KEY = os.getenv('APCA_API_KEY_ID', '')
    ALPACA_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY', '')
    ALPACA_BASE_URL = os.getenv('APCA_API_BASE_URL', 'https://paper-api.alpaca.markets')

    # Trading Strategy Parameters
    TRADING_SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
    MAX_POSITION_SIZE = 0.05  # 5% of total portfolio
    STOP_LOSS_PERCENT = 0.02  # 2% stop loss
    TAKE_PROFIT_PERCENT = 0.05  # 5% take profit

    # Risk Management
    MAX_TOTAL_RISK_PERCENT = 0.1  # 10% total portfolio risk
    CORRELATION_THRESHOLD = 0.7  # Stock correlation threshold

    # Logging and Monitoring
    LOG_LEVEL = 'INFO'
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

    # Machine Learning Model Parameters
    ML_MODEL_PATH = './ml_models/trading_model.pkl'
    FEATURE_COLUMNS = [
        'open', 'high', 'low', 'close', 'volume', 
        'rsi_14', 'macd', 'signal_line', 'bbands_upper', 'bbands_lower'
    ]

    @classmethod
    def validate(cls):
        """Validate critical configuration parameters"""
        if not cls.ALPACA_API_KEY or not cls.ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials are missing!")
        
        if len(cls.TRADING_SYMBOLS) == 0:
            raise ValueError("No trading symbols defined!")

        return True

# Validation on import
Config.validate()
