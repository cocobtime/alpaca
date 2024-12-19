import time
from collections import deque
from threading import Lock

class RateLimiter:
    """Token bucket rate limiter implementation"""
    def __init__(self, max_tokens, refill_rate, refill_period=1.0):
        """
        Initialize rate limiter
        :param max_tokens: Maximum number of tokens in the bucket
        :param refill_rate: Number of tokens to add per refill_period
        :param refill_period: Time period in seconds for token refill
        """
        self.max_tokens = float(max_tokens)
        self.refill_rate = float(refill_rate)
        self.refill_period = float(refill_period)
        
        self.tokens = self.max_tokens
        self.last_refill = time.time()
        self.lock = Lock()
        
        # Track API calls for monitoring and adaptive rate limiting
        self.calls_history = deque(maxlen=1000)
        self.error_history = deque(maxlen=100)
        
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        refill_amount = (elapsed / self.refill_period) * self.refill_rate
        
        self.tokens = min(self.max_tokens, self.tokens + refill_amount)
        self.last_refill = now
        
        # Adaptive rate adjustment based on error history
        recent_errors = sum(1 for t in self.error_history if now - t <= 60)
        if recent_errors > 5:  # If more than 5 errors in last minute
            self.tokens = min(self.tokens, self.max_tokens * 0.5)  # Reduce available tokens
    
    def acquire(self, tokens=1, wait=True):
        """
        Acquire tokens from the bucket
        :param tokens: Number of tokens to acquire
        :param wait: Whether to wait for tokens if not available
        :return: True if tokens were acquired, False otherwise
        """
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                self.calls_history.append(time.time())
                return True
            elif not wait:
                return False
            
            # Calculate wait time
            needed = tokens - self.tokens
            wait_time = (needed / self.refill_rate) * self.refill_period
            
            if wait_time > 0:
                time.sleep(wait_time)
                return self.acquire(tokens, wait)  # Try again after waiting
            
            return False
    
    def record_error(self):
        """Record an error occurrence"""
        with self.lock:
            self.error_history.append(time.time())

# Create rate limiters for different API endpoints with more conservative limits
RATE_LIMITERS = {
    'market_data': RateLimiter(max_tokens=50, refill_rate=50, refill_period=60),  # 50 calls per minute
    'account': RateLimiter(max_tokens=25, refill_rate=25, refill_period=60),      # 25 calls per minute
    'orders': RateLimiter(max_tokens=10, refill_rate=10, refill_period=60),       # 10 calls per minute
    'positions': RateLimiter(max_tokens=15, refill_rate=15, refill_period=60)     # 15 calls per minute
}
