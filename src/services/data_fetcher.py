from datetime import date, timedelta
from typing import List, Tuple, Optional
import yfinance as yf
import pandas as pd
import os
import contextlib

from ..models.stock_data import TransactionData
from . import db_service

def _fetch_with_suffix_handling(stock_code: str, start_date: date, end_date: date) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Fetches data from yfinance, automatically handling .TW and .TWO suffixes.
    It tries the .TW suffix first. If no data is returned, it tries .TWO.
    Returns the DataFrame and the successful ticker, or (None, None) on failure.
    """
    tickers_to_try = [f"{stock_code}.TW", f"{stock_code}.TWO"]
    for ticker in tickers_to_try:
        try:
            # Suppress yfinance's stderr output for expected "errors"
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stderr(devnull):
                    stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)
            if not stock_data.empty:
                return stock_data, ticker
        except Exception as e:
            # Still print genuine exceptions
            print(f"Could not fetch data for {ticker}: {e}")
            continue # Try the next ticker
    return None, None

def _convert_df_to_transaction_data(df: pd.DataFrame, stock_code: str) -> List[TransactionData]:
    """
    Converts a yfinance DataFrame to a list of TransactionData objects.
    """
    transactions = []
    for index, row in df.iterrows():
        transactions.append(TransactionData(
            stock_code=stock_code,
            date=index.date(),
            # The warning suggests that row['Open'] is a single-element Series.
            # Access the scalar value with .iloc[0] before casting.
            open_price=float(row['Open'].iloc[0]),
            close_price=float(row['Close'].iloc[0]),
            high_price=float(row['High'].iloc[0]),
            low_price=float(row['Low'].iloc[0]),
            volume=int(row['Volume'].iloc[0])
        ))
    return transactions

def fetch_stock_data(stock_code: str, fetch_date: date) -> List[TransactionData]:
    """
    Fetches transaction data for a given stock code and date using yfinance.
    It first checks the local database. If data is not found, it fetches from the web
    and saves the new data to the database.
    """
    # 1. Check local database first
    cached_data = db_service.get_transaction_data_by_date(stock_code, fetch_date)
    if cached_data:
        return [cached_data]

    # 2. If not in DB, fetch from the web using yfinance
    stock_data, _ = _fetch_with_suffix_handling(stock_code, start_date=fetch_date, end_date=fetch_date + timedelta(days=1))
    
    if stock_data is None or stock_data.empty:
        print(f"No data found for {stock_code} on {fetch_date}.")
        return []

    fetched_data = _convert_df_to_transaction_data(stock_data, stock_code)

    # 3. Save the newly fetched data to the database
    if fetched_data:
        db_service.save_transaction_data(fetched_data)
    
    return fetched_data

def fetch_stock_data_in_range(stock_code: str, start_date: date, end_date: date) -> List[TransactionData]:
    """
    Fetches transaction data for a given stock code and date range using yfinance.
    It checks the local database first. If data is incomplete, it fetches from the web
    for the required date range and backfills the database.
    """
    # 1. Check local database for the entire range
    cached_data = db_service.get_transaction_data_by_range(stock_code, start_date, end_date)
    
    # Note: This doesn't check for missing days within the range in the cache.
    # For now, we proceed to fetch the full range from the web.
    
    # 2. Fetch from the web for the required date range
    stock_data, _ = _fetch_with_suffix_handling(stock_code, start_date=start_date, end_date=end_date + timedelta(days=1))

    if stock_data is None or stock_data.empty:
        print(f"No data found for {stock_code} in range {start_date}-{end_date}.")
        return cached_data # Return what we have from the cache

    fetched_data = _convert_df_to_transaction_data(stock_data, stock_code)

    # 3. Save the newly fetched data to the database
    if fetched_data:
        db_service.save_transaction_data(fetched_data)
        # Re-query the database to return a complete and consistent list
        return db_service.get_transaction_data_by_range(stock_code, start_date, end_date)

    return cached_data
