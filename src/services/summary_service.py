from datetime import date, timedelta
from typing import List

from ..models.stock_data import TransactionData, WeeklySummary, MonthlySummary
from . import db_service

def get_past_week_data(stock_code: str, end_date: date) -> List[TransactionData]:
    """Retrieves all transaction data for a stock from the past week from the database."""
    start_date = end_date - timedelta(days=6)
    all_data = []
    current_date = start_date
    while current_date <= end_date:
        # Assuming fetch_stock_data will now primarily hit the cache for recent data
        data = db_service.get_transaction_data_by_date(stock_code, current_date)
        if data:
            all_data.append(data)
        current_date += timedelta(days=1)
    return all_data

def generate_weekly_summary(stock_code: str, today: date) -> WeeklySummary:
    """
    Generates a weekly summary for a given stock code ending on the given date.
    """
    end_date = today
    start_date = end_date - timedelta(days=6)
    
    weekly_data = get_past_week_data(stock_code, end_date)
    
    summary = WeeklySummary(
        stock_code=stock_code,
        start_date=start_date,
        end_date=end_date,
        data=weekly_data
    )
    
    return summary

def get_past_month_data(stock_code: str, year: int, month: int) -> List[TransactionData]:
    """Retrieves all transaction data for a stock for a specific month."""
    import calendar
    _, num_days = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, num_days)
    
    all_data = []
    current_date = start_date
    while current_date <= end_date:
        data = db_service.get_transaction_data_by_date(stock_code, current_date)
        if data:
            all_data.append(data)
        current_date += timedelta(days=1)
    return all_data

def generate_monthly_summary(stock_code: str, today: date) -> MonthlySummary:
    """
    Generates a monthly summary for the previous month.
    """
    # Logic to get the previous month
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    year = last_day_of_previous_month.year
    month = last_day_of_previous_month.month

    monthly_data = get_past_month_data(stock_code, year, month)

    summary = MonthlySummary(
        stock_code=stock_code,
        month=f"{year}-{month:02d}",
        data=monthly_data
    )

    return summary
