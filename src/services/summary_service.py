from datetime import date, timedelta
from typing import List

from ..models.stock_data import TransactionData, WeeklySummary, MonthlySummary
from . import data_fetcher, db_service

def get_data_for_date_range(
    stock_code: str, start_date: date, end_date: date
) -> List[TransactionData]:
    """Retrieves all transaction data for a stock for a given date range from the database."""
    all_data = []
    current_date = start_date
    while current_date <= end_date:
        # Assuming fetch_stock_data will now primarily hit the cache for recent data
        data = data_fetcher.fetch_stock_data(stock_code, current_date, silent=True)
        if data:
            all_data.extend(data)
        current_date += timedelta(days=1)
    return all_data


def generate_weekly_summary(stock_code: str, today: date) -> WeeklySummary:
    """
    Generates a weekly summary for a given stock code for the current week (Monday to Friday).
    """
    # Find the start of the week (Monday)
    start_of_week = today - timedelta(days=today.weekday())
    # Find the end of the week (Friday)
    end_of_week = start_of_week + timedelta(days=4)

    weekly_data = get_data_for_date_range(stock_code, start_of_week, end_of_week)

    summary = WeeklySummary(
        stock_code=stock_code,
        start_date=start_of_week,
        end_date=end_of_week,
        data=weekly_data
    )

    return summary

def get_past_month_data(
    stock_code: str, year: int, month: int
) -> List[TransactionData]:
    """Retrieves all transaction data for a stock for a specific month."""
    import calendar

    _, num_days = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, num_days)

    all_data = []
    current_date = start_date
    while current_date <= end_date:
        data = data_fetcher.fetch_stock_data(stock_code, current_date, silent=True)
        if data:
            all_data.extend(data)
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

def display_date_range_data(stock_code: str, start_date: date, end_date: date):
    """Fetches and displays transaction data for a given stock and date range."""
    print(f"--- Transaction Data for {stock_code} from {start_date} to {end_date} ---")
    
    data = data_fetcher.fetch_stock_data_in_range(stock_code, start_date, end_date)
    
    if data:
        import pandas as pd
        df = pd.DataFrame(data)
        print(df.to_string(index=False))
    else:
        print("No data found for the specified date range.")

