# Alpaca Trading Bot

A real-time algorithmic trading system using the Alpaca API, featuring automated trading strategies, risk management, and a web-based monitoring interface.

## Features

### Core Components
- Real-time trading automation
- Live balance and portfolio tracking
- Web-based monitoring dashboard
- Configurable trading strategies
- Risk management system

### Technical Features
- Flask-based web interface with WebSocket support
- Real-time account monitoring
- Market hours detection (Regular/Extended/Closed)
- Rate limiting and error handling
- Comprehensive logging system

### Risk Management
- Dynamic position sizing
- Balance tracking and monitoring
- Real-time performance metrics
- Error handling and retry mechanisms
- Rate limit management

### Monitoring & Analytics
- Real-time balance updates
- Position and order tracking
- Performance metrics calculation
- Hourly and daily change tracking
- WebSocket-based live updates

## Requirements
- Python 3.8+
- Alpaca API Keys (paper or live trading)
- Required packages:
  - alpaca-trade-api
  - numpy
  - pandas
  - python-dotenv
  - TA-Lib
  - scikit-learn
  - loguru
  - Flask
  - Flask-SocketIO

## Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy .env.template to .env
- Fill in your Alpaca API credentials:
```env
APCA_API_KEY_ID='your-api-key'
APCA_API_SECRET_KEY='your-secret-key'
APCA_API_BASE_URL='https://paper-api.alpaca.markets'  # or live API URL
```

## Usage

1. Start the trading bot with web interface:
```bash
python app.py
```

2. Run the trading bot without web interface:
```bash
./run_bot.sh
```

3. Access the web dashboard:
```
http://localhost:5000
```

## Project Structure

- `app.py`: Flask web application and WebSocket server
- `trading_bot.py`: Main trading bot implementation
- `balance_tracker.py`: Account and balance monitoring
- `indicators.py`: Technical analysis indicators
- `risk_manager.py`: Risk management system
- `models.py`: Database models
- `config.py`: Configuration settings
- `utils/`: Utility functions and helpers

## Web Interface Features

- Real-time account balance display
- Current positions and open orders
- Performance metrics (hourly/daily changes)
- Market status indicator
- Live trade notifications
- Performance analytics

## Rate Limiting

The system includes built-in rate limiting to comply with Alpaca API restrictions:
- Automatic retry mechanism
- Exponential backoff
- Request queuing
- Error handling for rate limit exceptions

## Warning

This trading bot is for educational and research purposes. Always test thoroughly with paper trading before using real funds. Trading involves significant risk of loss.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit pull requests.
