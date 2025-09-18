import argparse
from datetime import date
import pandas as pd

from src.services import data_fetcher, summary_service
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

    if args.weekly:
        print(f"--- Weekly Summary for Week Ending {today} ---")
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
        for code in stock_codes:
            summary = summary_service.generate_monthly_summary(code, today)
            print(f"\nStock: {code} (Month: {summary.month})")
            if summary.data:
                df = pd.DataFrame(summary.data)
                print(df.to_string(index=False))
            else:
                print("No data found for this period.")

    else: # Daily data
        print(f"--- Daily Transaction Data for {today} ---")
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
