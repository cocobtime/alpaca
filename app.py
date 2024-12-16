import os

# Set Alpaca API environment variables
os.environ['ALPACA_API_KEY'] = "PKY2G5O6O2XDO493SU2X"
os.environ['ALPACA_SECRET_KEY'] = "vm3aV23EKDCZA7EKUTmKPvpsVc1hdhf52yNXLDrv"

from flask import Flask, render_template
from flask_socketio import SocketIO
from trading_bot import TradingBot
from balance_tracker import BalanceTracker
import threading
import time
import logging
from datetime import datetime
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging to emit to WebSocket and console
class SocketIOHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        socketio.emit('log_message', {
            'timestamp': datetime.now().isoformat(),
            'message': msg
        })

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.addHandler(SocketIOHandler())

# Global variables
tracker = None

@app.route('/')
def index():
    return render_template('index.html')

def bot_thread(bot, symbols):
    """Thread function to run the trading bot"""
    bot.run(symbols)

def balance_thread(tracker):
    """Thread function to run the balance tracker"""
    # Send initial balance update immediately
    try:
        info = tracker.get_account_info()
        if info:
            print(f"[Server] Balance thread - Initial balance update: {json.dumps(info, indent=2)}")
            socketio.emit('balance_update', info)
    except Exception as e:
        logging.error(f"Error in initial balance update: {str(e)}")
        print(f"[Server] Initial balance error: {str(e)}")

    # Then continue with regular updates
    while True:
        try:
            time.sleep(10)  # Update every 10 seconds
            info = tracker.get_account_info()
            if info:
                print(f"[Server] Balance thread - Emitting balance update: {json.dumps(info, indent=2)}")
                socketio.emit('balance_update', info)
        except Exception as e:
            logging.error(f"Error in balance thread: {str(e)}")
            print(f"[Server] Balance thread error: {str(e)}")
            time.sleep(10)

@socketio.on('connect')
def handle_connect():
    print('[Server] Client connected')
    # Send initial balance update
    if tracker:
        try:
            def send_balance():
                info = tracker.get_account_info()
                if info:
                    print(f"[Server] Connect handler - Sending initial balance: {json.dumps(info, indent=2)}")
                    socketio.emit('balance_update', info)
                else:
                    print("[Server] Connect handler - No balance info available")
            
            # Delay the initial balance update by 1 second
            socketio.start_background_task(send_balance)
            
        except Exception as e:
            print(f"[Server] Connect handler error: {str(e)}")

@socketio.on('request_balance')
def handle_balance_request():
    print('[Server] Balance update requested')
    if tracker:
        try:
            info = tracker.get_account_info()
            if info:
                print(f"[Server] Balance request handler - Sending balance: {json.dumps(info, indent=2)}")
                socketio.emit('balance_update', info)
            else:
                print("[Server] Balance request handler - No balance info available")
        except Exception as e:
            print(f"[Server] Balance request handler error: {str(e)}")

if __name__ == '__main__':
    print("[Server] Starting application...")
    
    # Create balance tracker instance first
    print("[Server] Creating balance tracker...")
    tracker = BalanceTracker(
        api_key=os.environ['ALPACA_API_KEY'],
        api_secret=os.environ['ALPACA_SECRET_KEY'],
        base_url="https://paper-api.alpaca.markets"
    )
    
    # Test initial balance fetch
    try:
        initial_info = tracker.get_account_info()
        print(f"[Server] Initial balance check: {json.dumps(initial_info, indent=2)}")
    except Exception as e:
        print(f"[Server] Error checking initial balance: {str(e)}")
    
    # Create trading bot instance
    print("[Server] Creating trading bot...")
    bot = TradingBot(
        api_key=os.environ['ALPACA_API_KEY'],
        api_secret=os.environ['ALPACA_SECRET_KEY'],
        base_url="https://paper-api.alpaca.markets",
        socketio=socketio
    )
    
    # Get list of tradable symbols
    assets = bot.api.list_assets()
    tradable_symbols = [asset.symbol for asset in assets if asset.tradable]
    trading_symbols = tradable_symbols[:10]
    
    print("[Server] Starting threads...")
    
    # Start balance tracker in a separate thread
    balance_thread_instance = threading.Thread(target=balance_thread, args=(tracker,))
    balance_thread_instance.daemon = True
    balance_thread_instance.start()
    
    # Start bot in a separate thread
    bot_thread_instance = threading.Thread(target=bot_thread, args=(bot, trading_symbols))
    bot_thread_instance.daemon = True
    bot_thread_instance.start()
    
    print("[Server] Starting Flask-SocketIO on port 5001...")
    # Start Flask-SocketIO
    socketio.run(app, debug=True, use_reloader=False, port=5001, allow_unsafe_werkzeug=True)
