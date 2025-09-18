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
