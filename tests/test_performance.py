import unittest
import os
import sys
import time
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading_bot import MockTradingBot
from balance_tracker import BalanceTracker
from app import app

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.api_key = 'test_key'
        self.api_secret = 'test_secret'
        self.base_url = 'https://paper-api.alpaca.markets'

    def test_concurrent_requests(self):
        """Test handling of concurrent API requests"""
        num_threads = 10
        requests_per_thread = 5

        def make_requests(tracker):
            for _ in range(requests_per_thread):
                info = tracker.get_account_info()
                self.assertIsNotNone(info)
                time.sleep(0.1)  # Simulate real-world delay

        with patch('alpaca_trade_api.REST') as mock_api:
            # Mock API responses
            mock_api.return_value.get_account.return_value = Mock(
                portfolio_value='10000.00',
                cash='5000.00',
                buying_power='5000.00'
            )
            mock_api.return_value.list_positions.return_value = []
            mock_api.return_value.list_orders.return_value = []

            tracker = BalanceTracker(self.api_key, self.api_secret, self.base_url)
            threads = []

            start_time = time.time()

            # Create and start threads
            for _ in range(num_threads):
                thread = threading.Thread(target=make_requests, args=(tracker,))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            duration = time.time() - start_time
            requests_per_second = (num_threads * requests_per_thread) / duration

            print(f"\nPerformance Results:")
            print(f"Total Requests: {num_threads * requests_per_thread}")
            print(f"Duration: {duration:.2f} seconds")
            print(f"Requests/second: {requests_per_second:.2f}")

    def test_memory_usage(self):
        """Test memory usage under load"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB

        # Create multiple instances and generate load
        bots = []
        trackers = []
        num_instances = 5

        with patch('alpaca_trade_api.REST') as mock_api:
            # Mock API responses
            mock_api.return_value.get_account.return_value = Mock(
                portfolio_value='10000.00',
                cash='5000.00',
                buying_power='5000.00'
            )

            for _ in range(num_instances):
                bot = MockTradingBot()
                tracker = BalanceTracker(self.api_key, self.api_secret, self.base_url)
                bots.append(bot)
                trackers.append(tracker)

                # Generate some load
                bot.simulate_trading()
                tracker.get_account_info()

        final_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
        memory_increase = final_memory - initial_memory

        print(f"\nMemory Usage:")
        print(f"Initial Memory: {initial_memory:.2f} MB")
        print(f"Final Memory: {final_memory:.2f} MB")
        print(f"Memory Increase: {memory_increase:.2f} MB")

        # Assert reasonable memory usage
        self.assertLess(memory_increase, 100)  # Memory increase should be less than 100MB

    def test_response_times(self):
        """Test API response times"""
        num_requests = 50
        response_times = []

        with patch('alpaca_trade_api.REST') as mock_api:
            # Mock API responses
            mock_api.return_value.get_account.return_value = Mock(
                portfolio_value='10000.00',
                cash='5000.00',
                buying_power='5000.00'
            )

            tracker = BalanceTracker(self.api_key, self.api_secret, self.base_url)

            for _ in range(num_requests):
                start_time = time.time()
                tracker.get_account_info()
                response_time = time.time() - start_time
                response_times.append(response_time)

        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)

        print(f"\nResponse Times:")
        print(f"Average: {avg_response_time:.3f} seconds")
        print(f"Maximum: {max_response_time:.3f} seconds")
        print(f"Minimum: {min_response_time:.3f} seconds")

        # Assert reasonable response times
        self.assertLess(avg_response_time, 0.1)  # Average should be under 100ms
        self.assertLess(max_response_time, 0.5)  # Max should be under 500ms

if __name__ == '__main__':
    unittest.main()
