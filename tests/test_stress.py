import unittest
import os
import sys
import time
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor
import threading
import queue

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading_bot import MockTradingBot
from balance_tracker import BalanceTracker
from app import app

class TestStress(unittest.TestCase):
    def setUp(self):
        self.api_key = 'test_key'
        self.api_secret = 'test_secret'
        self.base_url = 'https://paper-api.alpaca.markets'
        
        # Configure test client
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_high_frequency_trading(self):
        """Test system under high-frequency trading conditions"""
        num_trades = 1000
        trade_queue = queue.Queue()
        error_queue = queue.Queue()

        def execute_trades(bot, num):
            try:
                for _ in range(num):
                    bot.simulate_trading()
                    trade_queue.put(1)
                    time.sleep(0.001)  # Simulate 1ms between trades
            except Exception as e:
                error_queue.put(str(e))

        with patch('alpaca_trade_api.REST') as mock_api:
            # Mock API responses
            mock_api.return_value.get_account.return_value = Mock(
                portfolio_value='10000.00',
                cash='5000.00',
                buying_power='5000.00'
            )

            bot = MockTradingBot()
            start_time = time.time()

            # Start trading thread
            trade_thread = threading.Thread(
                target=execute_trades,
                args=(bot, num_trades)
            )
            trade_thread.start()

            # Monitor progress
            completed_trades = 0
            while completed_trades < num_trades:
                try:
                    trade_queue.get(timeout=0.1)
                    completed_trades += 1
                except queue.Empty:
                    continue

                if not error_queue.empty():
                    errors = []
                    while not error_queue.empty():
                        errors.append(error_queue.get())
                    raise Exception(f"Trading errors occurred: {errors}")

            trade_thread.join()
            duration = time.time() - start_time

            trades_per_second = num_trades / duration
            print(f"\nHigh Frequency Trading Results:")
            print(f"Completed Trades: {completed_trades}")
            print(f"Duration: {duration:.2f} seconds")
            print(f"Trades/second: {trades_per_second:.2f}")

    def test_concurrent_users(self):
        """Test system with multiple concurrent users"""
        num_users = 50
        requests_per_user = 20
        response_times = queue.Queue()
        error_queue = queue.Queue()

        def simulate_user_activity(user_id):
            try:
                for _ in range(requests_per_user):
                    start_time = time.time()
                    response = self.client.get('/')
                    duration = time.time() - start_time

                    self.assertEqual(response.status_code, 200)
                    response_times.put(duration)
                    time.sleep(0.05)  # Simulate user think time
            except Exception as e:
                error_queue.put(f"User {user_id}: {str(e)}")

        start_time = time.time()
        threads = []

        # Start user threads
        for i in range(num_users):
            thread = threading.Thread(
                target=simulate_user_activity,
                args=(i,)
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        duration = time.time() - start_time

        # Check for errors
        if not error_queue.empty():
            errors = []
            while not error_queue.empty():
                errors.append(error_queue.get())
            raise Exception(f"User simulation errors occurred: {errors}")

        # Calculate statistics
        times = []
        while not response_times.empty():
            times.append(response_times.get())

        avg_response_time = sum(times) / len(times)
        max_response_time = max(times)
        requests_per_second = (num_users * requests_per_user) / duration

        print(f"\nConcurrent Users Test Results:")
        print(f"Number of Users: {num_users}")
        print(f"Total Requests: {num_users * requests_per_user}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Requests/second: {requests_per_second:.2f}")
        print(f"Average Response Time: {avg_response_time:.3f} seconds")
        print(f"Max Response Time: {max_response_time:.3f} seconds")

    def test_error_recovery(self):
        """Test system's ability to recover from errors"""
        num_requests = 100
        error_frequency = 0.2  # 20% error rate
        recovery_times = []

        with patch('alpaca_trade_api.REST') as mock_api:
            def api_with_errors(*args, **kwargs):
                if random.random() < error_frequency:
                    raise Exception("Simulated API Error")
                return Mock(
                    portfolio_value='10000.00',
                    cash='5000.00',
                    buying_power='5000.00'
                )

            mock_api.return_value.get_account.side_effect = api_with_errors
            tracker = BalanceTracker(self.api_key, self.api_secret, self.base_url)

            for _ in range(num_requests):
                start_time = time.time()
                try:
                    info = tracker.get_account_info()
                    if info is not None:
                        recovery_time = time.time() - start_time
                        recovery_times.append(recovery_time)
                except Exception:
                    pass

        avg_recovery_time = sum(recovery_times) / len(recovery_times)
        max_recovery_time = max(recovery_times)

        print(f"\nError Recovery Test Results:")
        print(f"Total Requests: {num_requests}")
        print(f"Average Recovery Time: {avg_recovery_time:.3f} seconds")
        print(f"Max Recovery Time: {max_recovery_time:.3f} seconds")

if __name__ == '__main__':
    unittest.main()
