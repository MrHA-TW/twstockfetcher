import sqlite3
from datetime import date
from typing import List, Optional

from ..models.stock_data import TransactionData

DB_PATH = "stock_data.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    """Initializes the database and creates the transaction_data table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaction_data (
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL,
            date TEXT NOT NULL,
            open_price REAL NOT NULL,
            close_price REAL NOT NULL,
            high_price REAL NOT NULL,
            low_price REAL NOT NULL,
            volume INTEGER NOT NULL,
            PRIMARY KEY (stock_code, date)
        );
    """)
    conn.commit()
    conn.close()

def save_transaction_data(data: List[TransactionData]):
    """Saves a list of TransactionData objects to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    data_to_insert = [
        (
            d.stock_code, 
            d.stock_name,
            d.date.isoformat(), 
            d.open_price, 
            d.close_price, 
            d.high_price, 
            d.low_price, 
            d.volume
        ) 
        for d in data
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO transaction_data (stock_code, stock_name, date, open_price, close_price, high_price, low_price, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, data_to_insert)
    
    conn.commit()
    conn.close()

def get_transaction_data_by_date(stock_code: str, target_date: date) -> Optional[TransactionData]:
    """Retrieves transaction data for a specific stock and date from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM transaction_data
        WHERE stock_code = ? AND date = ?
    """, (stock_code, target_date.isoformat()))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return TransactionData(
            stock_code=row['stock_code'],
            stock_name=row['stock_name'],
            date=date.fromisoformat(row['date']),
            open_price=row['open_price'],
            close_price=row['close_price'],
            high_price=row['high_price'],
            low_price=row['low_price'],
            volume=row['volume']
        )
    return None

def get_transaction_data_by_range(stock_code: str, start_date: date, end_date: date) -> List[TransactionData]:
    """Retrieves all transaction data for a specific stock within a date range."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM transaction_data
        WHERE stock_code = ? AND date BETWEEN ? AND ?
        ORDER BY date ASC
    """, (stock_code, start_date.isoformat(), end_date.isoformat()))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        TransactionData(
            stock_code=row['stock_code'],
            stock_name=row['stock_name'],
            date=date.fromisoformat(row['date']),
            open_price=row['open_price'],
            close_price=row['close_price'],
            high_price=row['high_price'],
            low_price=row['low_price'],
            volume=row['volume']
        ) for row in rows
    ]
