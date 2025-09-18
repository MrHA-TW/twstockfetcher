import argparse
from datetime import date
import pandas as pd

from src.services import data_fetcher
from src.services import db_service # Import db_service to initialize the DB

def main():
    """Main function to handle CLI arguments and orchestrate the data fetching and display."""
    # Initialize the database at the start of the application
    db_service.initialize_db()

    parser = argparse.ArgumentParser(description="Fetch Taiwan stock market data.")
    parser.add_argument(
        '--stocks',
        type=str,
        required=True,
        help='Comma-separated list of stock codes (e.g., "2330,2317").'
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
    stock_codes = [code.strip() for code in args.stocks.split(',')]
    today = date.today()

    if not args.weekly and not args.monthly:
        print(f"--- Daily Transaction Data for {today} ---")
        all_data = []
        for code in stock_codes:
            data = data_fetcher.fetch_stock_data(code, today)
            if data:
                all_data.extend(data)
        
        if all_data:
            df = pd.DataFrame(all_data)
            print(df.to_string(index=False))
        else:
            print("No data found for the specified stocks on this date.")

    # Placeholder for weekly/monthly summary logic
    if args.weekly:
        print("Weekly summary not yet implemented.")

    if args.monthly:
        print("Monthly summary not yet implemented.")


if __name__ == "__main__":
    main()
