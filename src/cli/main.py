import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import argparse
import sys
from datetime import date, datetime
import pandas as pd

from src.services import data_fetcher, summary_service
from src.services import db_service # Import db_service to initialize the DB

def _validate_and_parse_date(date_str: str) -> date:
    """Parses a date string and validates that it strictly matches the YYYY-MM-DD format."""
    dt_obj = datetime.strptime(date_str, "%Y-%m-%d")
    if dt_obj.strftime("%Y-%m-%d") != date_str:
        raise ValueError("Date format is not strictly YYYY-MM-DD.")
    return dt_obj.date()

def main():
    """Main function to handle CLI arguments and orchestrate the data fetching and display."""
    # Initialize the database at the start of the application
    db_service.initialize_db()

    parser = argparse.ArgumentParser(description="Fetch Taiwan stock market data.")
    parser.add_argument(
        '--stocks',
        type=str,
        help='Comma-separated list of stock codes (e.g., "2330,2317").'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date for query (YYYY-MM-DD).'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        help='End date for query (YYYY-MM-DD).'
    )
    parser.add_argument(
        '--weekly',
        action='store_true',
        help='Get a summary for the past week.'
    )
    parser.add_argument(
        '--monthly',
        action='store_true',
        help='Get a summary for the past month.'
    )
    parser.add_argument(
        '--info',
        action='store_true',
        help='Get key investment metrics for a stock.'
    )

    args = parser.parse_args()
    today = date.today()

    if args.info:
        if not args.stocks:
            print("Error: --stocks is required with --info", file=sys.stderr)
            sys.exit(1)
        stock_codes = [code.strip() for code in args.stocks.split(',')]
        for code in stock_codes:
            summary_service.display_stock_info(code)

    elif args.start_date:
        try:
            stock_codes_str = args.stocks
            if not stock_codes_str:
                print("Error: --stocks is required with --start-date", file=sys.stderr)
                sys.exit(1)
            
            stock_codes = [code.strip() for code in stock_codes_str.split(',')]
            start_date = _validate_and_parse_date(args.start_date)
            end_date = _validate_and_parse_date(args.end_date) if args.end_date else date.today()
        except (ValueError, TypeError):
            print("Invalid date format. Please use YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)

        if start_date > end_date:
            print("Start date cannot be after end date.", file=sys.stderr)
            sys.exit(1)

        for stock_code in stock_codes:
            summary_service.display_date_range_data(
                stock_code=stock_code,
                start_date=start_date,
                end_date=end_date
            )

    elif args.weekly:
        print(f"--- Weekly Summary for Week Ending {today} ---")
        stock_codes = [code.strip() for code in args.stocks.split(',')]
        for code in stock_codes:
            summary = summary_service.generate_weekly_summary(code, today)
            if summary.data:
                df = pd.DataFrame(summary.data)
                # Reorder columns to place stock_name after stock_code
                cols = ['stock_code', 'stock_name', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
                df_cols = [col for col in cols if col in df.columns]
                df = df[df_cols]
                print(df.to_string(index=False))
            else:
                print("No data found for this period.")
    
    elif args.monthly:
        print(f"--- Monthly Summary ---")
        stock_codes = [code.strip() for code in args.stocks.split(',')]
        for code in stock_codes:
            summary = summary_service.generate_monthly_summary(code, today)
            print(f"\nStock: {code} (Month: {summary.month})")
            if summary.data:
                df = pd.DataFrame(summary.data)
                # Reorder columns to place stock_name after stock_code
                cols = ['stock_code', 'stock_name', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
                df_cols = [col for col in cols if col in df.columns]
                df = df[df_cols]
                print(df.to_string(index=False))
            else:
                print("No data found for this period.")

    elif args.stocks: # Daily data
        print(f"--- Daily Transaction Data for {today} ---")
        stock_codes = [code.strip() for code in args.stocks.split(',')]
        all_data = []
        for code in stock_codes:
            # For daily, we might need to fetch if not in DB
            # The fetch_stock_data function handles caching
            data = data_fetcher.fetch_stock_data(code, today)
            if data:
                all_data.extend(data)
        
        if all_data:
            df = pd.DataFrame(all_data)
            # Reorder columns to place stock_name after stock_code
            cols = ['stock_code', 'stock_name', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
            df_cols = [col for col in cols if col in df.columns]
            df = df[df_cols]
            print(df.to_string(index=False))
        else:
            print("No data found for the specified stocks on this date.")

if __name__ == "__main__":
    main()
