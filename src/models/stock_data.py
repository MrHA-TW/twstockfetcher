from dataclasses import dataclass
from datetime import date
from typing import List

@dataclass
class Stock:
    """Represents a stock in the Taiwan stock market."""
    stock_code: str
    stock_name: str

@dataclass
class TransactionData:
    """Represents the daily transaction data for a stock."""
    stock_code: str
    date: date
    open_price: float
    close_price: float
    high_price: float
    low_price: float
    volume: int

@dataclass
class WeeklySummary:
    """Represents the summary of transaction data for a week."""
    stock_code: str
    start_date: date
    end_date: date
    data: List[TransactionData]

@dataclass
class MonthlySummary:
    """Represents the summary of transaction data for a month."""
    stock_code: str
    month: str  # e.g., "2025-09"
    data: List[TransactionData]
