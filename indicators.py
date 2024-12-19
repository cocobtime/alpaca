import numpy as np
from typing import List, Dict, Union
import pandas as pd

class TechnicalIndicators:
    """
    A class that calculates various technical indicators.
    """
    @staticmethod
    def calculate_moving_averages(prices: List[float], short_window: int = 5, long_window: int = 20) -> Dict[str, float]:
        """Calculate short and long-term moving averages.

        Args:
            prices (List[float]): A list of prices.
            short_window (int, optional): The short-term window. Defaults to 5.
            long_window (int, optional): The long-term window. Defaults to 20.

        Returns:
            Dict[str, float]: A dictionary containing the short and long-term moving averages.
        """
        if len(prices) < long_window:
            return {"sma_short": prices[-1], "sma_long": prices[-1]}
        
        prices_array = np.array(prices)
        sma_short = np.mean(prices_array[-short_window:])
        sma_long = np.mean(prices_array[-long_window:])
        
        return {
            "sma_short": sma_short,
            "sma_long": sma_long
        }

    @staticmethod
    def calculate_volatility(prices: List[float], window: int = 20) -> float:
        """Calculate price volatility using standard deviation.

        Args:
            prices (List[float]): A list of prices.
            window (int, optional): The window for calculating volatility. Defaults to 20.

        Returns:
            float: The calculated volatility.
        """
        if len(prices) < window:
            return 0.0
        
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns[-window:]) * np.sqrt(252)  # Annualized volatility
        return volatility

    @staticmethod
    def calculate_atr(high: List[float], low: List[float], close: List[float], period: int = 14) -> float:
        """Calculate Average True Range (ATR).

        Args:
            high (List[float]): A list of high prices.
            low (List[float]): A list of low prices.
            close (List[float]): A list of close prices.
            period (int, optional): The period for calculating ATR. Defaults to 14.

        Returns:
            float: The calculated ATR.
        """
        if len(high) < 2:
            return 0.0
        
        tr_list = []
        for i in range(1, len(high)):
            tr = max(
                high[i] - low[i],  # Current high - current low
                abs(high[i] - close[i-1]),  # Current high - previous close
                abs(low[i] - close[i-1])  # Current low - previous close
            )
            tr_list.append(tr)
        
        if not tr_list:
            return 0.0
            
        atr = np.mean(tr_list[-period:])
        return atr

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index (RSI).

        Args:
            prices (List[float]): A list of prices.
            period (int, optional): The period for calculating RSI. Defaults to 14.

        Returns:
            float: The calculated RSI.
        """
        if len(prices) < period + 1:
            return 50.0
        
        # Calculate price changes
        delta = np.diff(prices)
        
        # Separate gains and losses
        gains = np.where(delta > 0, delta, 0)
        losses = np.where(delta < 0, -delta, 0)
        
        # Calculate average gains and losses
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

    @staticmethod
    def calculate_macd(prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, float]:
        """Calculate MACD (Moving Average Convergence Divergence).

        Args:
            prices (List[float]): A list of prices.
            fast_period (int, optional): The fast period for MACD. Defaults to 12.
            slow_period (int, optional): The slow period for MACD. Defaults to 26.
            signal_period (int, optional): The signal period for MACD. Defaults to 9.

        Returns:
            Dict[str, float]: A dictionary containing the MACD line, signal line, and histogram.
        """
        if len(prices) < slow_period:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}
        
        # Calculate EMAs
        ema_fast = pd.Series(prices).ewm(span=fast_period, adjust=False).mean().iloc[-1]
        ema_slow = pd.Series(prices).ewm(span=slow_period, adjust=False).mean().iloc[-1]
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        macd_series = pd.Series(prices).ewm(span=fast_period, adjust=False).mean() - \
                     pd.Series(prices).ewm(span=slow_period, adjust=False).mean()
        signal_line = macd_series.ewm(span=signal_period, adjust=False).mean().iloc[-1]
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }

    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, num_std: float = 2.0) -> Dict[str, float]:
        """Calculate Bollinger Bands.

        Args:
            prices (List[float]): A list of prices.
            period (int, optional): The period for calculating Bollinger Bands. Defaults to 20.
            num_std (float, optional): The number of standard deviations for Bollinger Bands. Defaults to 2.0.

        Returns:
            Dict[str, float]: A dictionary containing the upper, middle, and lower Bollinger Bands.
        """
        if len(prices) < period:
            return {"upper": prices[-1], "middle": prices[-1], "lower": prices[-1]}
        
        prices_array = np.array(prices[-period:])
        middle_band = np.mean(prices_array)
        std_dev = np.std(prices_array)
        
        upper_band = middle_band + (std_dev * num_std)
        lower_band = middle_band - (std_dev * num_std)
        
        return {
            "upper": upper_band,
            "middle": middle_band,
            "lower": lower_band
        }

    @staticmethod
    def calculate_volume_profile(prices: List[float], volumes: List[float], num_bins: int = 10) -> Dict[str, float]:
        """Calculate Volume Profile.

        Args:
            prices (List[float]): A list of prices.
            volumes (List[float]): A list of volumes.
            num_bins (int, optional): The number of bins for the volume profile. Defaults to 10.

        Returns:
            Dict[str, float]: A dictionary containing the Point of Control (POC), Value Area High, and Value Area Low.
        """
        if not prices or not volumes:
            return {"poc": 0.0, "va_high": 0.0, "va_low": 0.0}
        
        # Create price bins
        price_bins = np.linspace(min(prices), max(prices), num_bins)
        volume_per_bin, _ = np.histogram(prices, bins=price_bins, weights=volumes)
        
        # Find Point of Control (price level with highest volume)
        poc_index = np.argmax(volume_per_bin)
        poc = (price_bins[poc_index] + price_bins[poc_index + 1]) / 2
        
        # Calculate Value Area (70% of volume)
        total_volume = np.sum(volume_per_bin)
        target_volume = total_volume * 0.7
        
        cumsum_volume = np.cumsum(sorted(volume_per_bin, reverse=True))
        value_area_threshold = np.searchsorted(cumsum_volume, target_volume)
        
        va_high = np.percentile(prices, 85)
        va_low = np.percentile(prices, 15)
        
        return {
            "poc": poc,  # Point of Control
            "va_high": va_high,  # Value Area High
            "va_low": va_low  # Value Area Low
        }

    @staticmethod
    def get_market_session(timestamp: pd.Timestamp) -> str:
        """Determine market session based on time.

        Args:
            timestamp (pd.Timestamp): The timestamp to determine the market session for.

        Returns:
            str: The market session ("closed", "pre_market", "opening", "mid_day", "closing", "after_hours").
        """
        hour = timestamp.hour
        
        if hour < 4:
            return "closed"
        elif 4 <= hour < 9:
            return "pre_market"
        elif 9 <= hour < 10:
            return "opening"
        elif 10 <= hour < 15:
            return "mid_day"
        elif 15 <= hour < 16:
            return "closing"
        elif 16 <= hour < 20:
            return "after_hours"
        else:
            return "closed"
