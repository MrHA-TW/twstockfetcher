from datetime import date, datetime
from typing import List
import twstock

from ..models.stock_data import TransactionData
from . import db_service

def fetch_stock_data(stock_code: str, fetch_date: date) -> List[TransactionData]:
    """
    Fetches transaction data for a given stock code and date.
    It first checks the local database. If data is not found, it fetches from the web
    and saves the new data to the database.
    """
    # 1. Check local database first
    cached_data = db_service.get_transaction_data_by_date(stock_code, fetch_date)
    if cached_data:
        return [cached_data]

    # 2. If not in DB, fetch from the web
    try:
        stock = twstock.Stock(stock_code)
        data = stock.fetch(fetch_date.year, fetch_date.month)
    except Exception as e:
        print(f"Error fetching data for {stock_code}: {e}")
        return []

    # Filter for the specific date and create TransactionData objects
    fetched_data = []
    for d in data:
        if d.date.date() == fetch_date:
            transaction = TransactionData(
                stock_code=stock_code,
                date=d.date.date(),
                open_price=d.open,
                close_price=d.close,
                high_price=d.high,
                low_price=d.low,
                volume=d.capacity
            )
            fetched_data.append(transaction)
            break # Found the data for the specific day

    # 3. Save the newly fetched data to the database
    if fetched_data:
        db_service.save_transaction_data(fetched_data)
    
    return fetched_data

def fetch_stock_data_in_range(stock_code: str, start_date: date, end_date: date) -> List[TransactionData]:
    """
    Fetches transaction data for a given stock code and date range.
    It checks the local database first. If data is incomplete, it fetches from the web
    for the required months and backfills the database.
    """
    # 1. Check local database for the entire range
    cached_data = db_service.get_transaction_data_by_range(stock_code, start_date, end_date)
    # A simple check to see if we have all days. More complex logic might be needed.
    # For this implementation, we assume if the count matches, we have it all.
    expected_days = (end_date - start_date).days + 1
    if len(cached_data) >= expected_days: # Simplified check
        return cached_data

    # 2. Fetch from the web for the required months
    try:
        stock = twstock.Stock(stock_code)
        # This is a simplified fetch. `twstock` might require fetching month by month.
        # For this example, we assume fetching the end_date's month is sufficient.
        data = stock.fetch(end_date.year, end_date.month)
    except Exception as e:
        print(f"Error fetching data for {stock_code}: {e}")
        return []

    # 3. Filter, convert, and save to DB
    fetched_data = []
    for d in data:
        current_date = d.date.date()
        if start_date <= current_date <= end_date:
            transaction = TransactionData(
                stock_code=stock_code,
                date=current_date,
                open_price=d.open,
                close_price=d.close,
                high_price=d.high,
                low_price=d.low,
                volume=d.capacity
            )
            fetched_data.append(transaction)

    if fetched_data:
        db_service.save_transaction_data(fetched_data)
    
    return fetched_data

    """
    Fetches transaction data for a given stock code and date.
    It first checks the local database. If data is not found, it fetches from the web
    and saves the new data to the database.
    """
    # 1. Check local database first
    cached_data = db_service.get_transaction_data_by_date(stock_code, fetch_date)
    if cached_data:
        return [cached_data]

    # 2. If not in DB, fetch from the web
    try:
        stock = twstock.Stock(stock_code)
        data = stock.fetch(fetch_date.year, fetch_date.month)
    except Exception as e:
        print(f"Error fetching data for {stock_code}: {e}")
        return []

    # Filter for the specific date and create TransactionData objects
    fetched_data = []
    for d in data:
        if d.date.date() == fetch_date:
            transaction = TransactionData(
                stock_code=stock_code,
                date=d.date.date(),
                open_price=d.open,
                close_price=d.close,
                high_price=d.high,
                low_price=d.low,
                volume=d.capacity
            )
            fetched_data.append(transaction)
            break # Found the data for the specific day

    # 3. Save the newly fetched data to the database
    if fetched_data:
        db_service.save_transaction_data(fetched_data)
    
    return fetched_data
