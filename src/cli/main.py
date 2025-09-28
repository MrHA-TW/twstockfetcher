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
        '--stock',
        type=str,
        help='A single stock code for date range queries (e.g., "2330").'
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

    args = parser.parse_args()
    today = date.today()

    if args.start_date:
        try:
            stock_code = args.stock
            if not stock_code:
                print("Error: --stock is required with --start-date", file=sys.stderr)
                sys.exit(1)
            start_date = _validate_and_parse_date(args.start_date)
            end_date = _validate_and_parse_date(args.end_date) if args.end_date else date.today()
        except (ValueError, TypeError):
            print("Invalid date format. Please use YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)

        if start_date > end_date:
            print("Start date cannot be after end date.", file=sys.stderr)
            sys.exit(1)

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
            print(f"\nStock: {code} ({summary.start_date} to {summary.end_date})")
            if summary.data:
                df = pd.DataFrame(summary.data)
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
            print(df.to_string(index=False))
        else:
            print("No data found for the specified stocks on this date.")

if __name__ == "__main__":
    main()
