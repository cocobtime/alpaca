# Alpaca Trading Bot with Balance Checker

A real-time trading bot and account balance monitoring system using the Alpaca API. This application includes a web dashboard that displays live account information and trading activities.

## Features

- Real-time account balance monitoring
- Live trading bot using Q-learning
- Web dashboard showing:
  - Total Equity
  - Cash Balance
  - Buying Power
  - Hourly and Daily P/L
  - Active Trades
  - Bot Actions Log

## Requirements

- Python 3.8+
- Alpaca API account (paper trading)
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/alpaca-balance-checker.git
cd alpaca-balance-checker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your Alpaca API credentials as environment variables:
```bash
export ALPACA_API_KEY="your_api_key"
export ALPACA_SECRET_KEY="your_secret_key"
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5001
```

## Configuration

- The trading bot parameters can be adjusted in `trading_bot.py`
- Balance update frequency can be modified in `balance_tracker.py`
- Web interface styling can be customized in `static/style.css`

## Security Note

Never commit your API keys to version control. Always use environment variables or a secure configuration file for sensitive credentials.

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
