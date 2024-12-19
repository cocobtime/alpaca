import os
from dotenv import load_dotenv
import config
import logging
from flask import Flask, render_template
from flask_socketio import SocketIO
from trading_bot import TradingBot
from balance_tracker import BalanceTracker
import threading
import time
from datetime import datetime
import json

# Load environment variables from .env file and config
load_dotenv()

# Use environment variables or defaults for Alpaca API
if not os.getenv('APCA_API_KEY_ID') or not os.getenv('APCA_API_SECRET_KEY'):
    print("[Server] Error: Alpaca API keys not found in environment variables. Please set them before running the application.")
    raise ValueError("Alpaca API keys not found in environment variables.")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging to emit to WebSocket and console
class SocketIOHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        socketio.emit('log_message', {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'message': msg
        })

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.addHandler(SocketIOHandler())

def get_market_status(api):
    """Get the current market status"""
    try:
        clock = api.get_clock()
        if clock and clock.is_open:
            if clock.next_close - datetime.now() > clock.next_open - datetime.now():
                return "REGULAR"
            else:
                return "EXTENDED"
        return "CLOSED"
    except Exception as e:
        logger.error(f"Error getting market status: {str(e)}")
        return "UNKNOWN"

@app.route('/')
def index():
    return render_template('index.html')

def bot_thread(bot, symbols):
    """Thread function to run the trading bot"""
    while True:
        try:
            bot.run_trading_cycle()
        except Exception as e:
            logger.error(f"Error in trading cycle: {str(e)}")
        time.sleep(60)  # Wait 1 minute between cycles

def balance_thread(tracker):
    """Thread function to run the balance tracker"""
    market_status = "UNKNOWN"
    while True:
        try:
            # Get account information
            account_info = tracker.get_account_info()
            if account_info:
                try:
                    # Get market status
                    new_market_status = get_market_status(tracker.api)
                    if new_market_status:
                        market_status = new_market_status
                except Exception as e:
                    logger.error(f"Error getting market status: {str(e)}")
                
                # Emit market status
                socketio.emit('market_status', {'status': market_status})
                
                # Emit balance update
                socketio.emit('balance_update', account_info)
                
                # Log important changes
                if account_info.get('daily_change', 0) < -100:
                    logger.warning(f"Large daily loss: ${account_info['daily_change']:.2f}")
                elif account_info.get('daily_change', 0) > 100:
                    logger.info(f"Large daily gain: ${account_info['daily_change']:.2f}")
            
            # Adjust sleep time based on market hours
            if market_status == "REGULAR":
                time.sleep(5)  # Update every 5 seconds during regular hours
            elif market_status == "EXTENDED":
                time.sleep(10)  # Update every 10 seconds during extended hours
            else:
                time.sleep(30)  # Update every 30 seconds when market is closed
                
        except Exception as e:
            logger.error(f"Error in balance thread: {str(e)}")
            time.sleep(5)

def refresh_tradable_symbols_periodically(bot):
    """Thread function to periodically refresh tradable symbols"""
    while True:
        try:
            bot.update_tradable_symbols()
        except Exception as e:
            logger.error(f"Error refreshing symbols: {str(e)}")
        time.sleep(3600)  # Refresh every hour

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected")

if __name__ == '__main__':
    print("[Server] Starting application...")
    
    # Create balance tracker instance
    tracker = BalanceTracker(
        api_key=os.getenv('APCA_API_KEY_ID'),
        api_secret=os.getenv('APCA_API_SECRET_KEY'),
        base_url=os.getenv('APCA_API_BASE_URL')
    )
    
    # Create trading bot instance
    bot = TradingBot(
        api_key=os.getenv('APCA_API_KEY_ID'),
        api_secret=os.getenv('APCA_API_SECRET_KEY'),
        base_url=os.getenv('APCA_API_BASE_URL')
    )
    
    # Start balance tracker thread
    balance_tracker_thread = threading.Thread(target=balance_thread, args=(tracker,))
    balance_tracker_thread.daemon = True
    balance_tracker_thread.start()
    
    # Start trading bot thread
    trading_bot_thread = threading.Thread(target=bot_thread, args=(bot, config.Config.TRADING_SYMBOLS))
    trading_bot_thread.daemon = True
    trading_bot_thread.start()
    
    # Start symbol refresh thread
    symbol_refresh_thread = threading.Thread(target=refresh_tradable_symbols_periodically, args=(bot,))
    symbol_refresh_thread.daemon = True
    symbol_refresh_thread.start()
    
    # Start Flask-SocketIO with unsafe Werkzeug allowed on port 5001
    socketio.run(app, debug=True, use_reloader=False, allow_unsafe_werkzeug=True, port=5001, host='0.0.0.0')
