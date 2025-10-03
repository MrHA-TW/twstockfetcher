import os
import contextlib
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
        # Reorder columns to place stock_name after stock_code
        cols = ['stock_code', 'stock_name', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
        df_cols = [col for col in cols if col in df.columns]
        df = df[df_cols]
        print(df.to_string(index=False))
    else:
        print("No data found for the specified date range.")


import yfinance as yf

def display_stock_info(stock_code: str):
    """Fetches and displays key investment metrics for a given stock code."""
    print(f"--- Key Investment Metrics for {stock_code} ---")
    
    ticker = None
    info = None
    
    # Try different suffixes for Taiwan stocks. The language of the info (e.g., Chinese for longName)
    # depends on the data source (Yahoo Finance) and is handled automatically.
    with open(os.devnull, 'w') as devnull:
        with contextlib.redirect_stderr(devnull):
            for suffix in [".TW", ".TWO", ""]:
                try:
                    temp_ticker = yf.Ticker(f"{stock_code}{suffix}")
                    # The 'info' attribute can be slow; check a lightweight attribute first
                    if temp_ticker.history(period="1d").empty:
                        continue
                    info = temp_ticker.info
                    # Check if we got meaningful data
                    if info and info.get('longName'):
                        ticker = temp_ticker
                        break
                except Exception:
                    continue

    if not ticker or not info:
        print(f"Could not retrieve information for stock code: {stock_code}")
        return

    key_metrics = {
        "公司名稱": info.get("longName"),
        "產業": info.get("industry"),
        "市值": f"{info.get('marketCap', 'N/A'):,}",
        "本益比": info.get("trailingPE"),
        "預期本益比": info.get("forwardPE"),
        "股價淨值比": info.get("priceToBook"),
        "股息殖利率": f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else "N/A",
        "Beta值": info.get("beta"),
        "目前股價": info.get("regularMarketPrice"),
        "52週最高價": info.get("fiftyTwoWeekHigh"),
        "52週最低價": info.get("fiftyTwoWeekLow"),
    }

    for key, value in key_metrics.items():
        print(f"{key+':':<20} {value if value is not None else 'N/A'}")

