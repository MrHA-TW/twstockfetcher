import os
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from datetime import date, datetime, timedelta

from src.cli import main
from src.models.stock_data import TransactionData, WeeklySummary, MonthlySummary
from src.services import db_service, data_fetcher


class TestCli(unittest.TestCase):

    def setUp(self):
        """Redirect stdout and stderr to capture output."""
        self.captured_output = StringIO()
        self.captured_stderr = StringIO()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = self.captured_output
        sys.stderr = self.captured_stderr

    def tearDown(self):
        """Restore stdout and stderr."""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

    @patch('src.cli.main.data_fetcher')
    @patch('src.cli.main.db_service')
    def test_daily_data_display(self, mock_db_service, mock_data_fetcher):
        """Test the CLI for displaying daily stock data."""
        # Arrange
        test_date = date.today()
        stock_code = "2330"
        
        mock_data = TransactionData(
            stock_code=stock_code, stock_name="TSMC", date=test_date, open_price=900.0, 
            close_price=905.0, high_price=910.0, low_price=899.0, volume=50000
        )
        mock_data_fetcher.fetch_stock_data.return_value = [mock_data]
        sys.argv = ['main.py', '--stocks', stock_code]
        
        # Act
        main.main()
        
        # Assert
        output = self.captured_output.getvalue()
        self.assertIn("--- Daily Transaction Data", output)
        self.assertIn(stock_code, output)
        self.assertIn("TSMC", output)
        mock_db_service.initialize_db.assert_called_once()

    @patch('src.cli.main.summary_service.generate_weekly_summary')
    @patch('src.cli.main.db_service')
    def test_weekly_summary_display(self, mock_db_service, mock_generate_weekly_summary):
        """Test the CLI for displaying weekly summary."""
        # Arrange
        test_date = date.today()
        stock_code = "2330"
        
        mock_summary_data = [
            {'stock_code': stock_code, 'stock_name': 'TSMC', 'date': test_date, 'open_price': 890.0, 'close_price': 905.0, 'high_price': 910.0, 'low_price': 888.0, 'volume': 45000}
        ]
        mock_summary = WeeklySummary(
            stock_code=stock_code,
            start_date=test_date - timedelta(days=test_date.weekday()),
            end_date=(test_date - timedelta(days=test_date.weekday())) + timedelta(days=4),
            data=mock_summary_data
        )
        
        mock_generate_weekly_summary.return_value = mock_summary
        sys.argv = ['main.py', '--stocks', stock_code, '--weekly']
        
        # Act
        main.main()
        
        # Assert
        output = self.captured_output.getvalue()
        self.assertIn("--- Weekly Summary", output)
        self.assertIn(stock_code, output)
        self.assertIn("TSMC", output)
        self.assertIn("905.0", output) # Check for close price
        mock_db_service.initialize_db.assert_called_once()
        mock_generate_weekly_summary.assert_called_once_with(stock_code, test_date)

    @patch('src.cli.main.summary_service.generate_monthly_summary')
    @patch('src.cli.main.db_service')
    def test_monthly_summary_display(self, mock_db_service, mock_generate_monthly_summary):
        """Test the CLI for displaying monthly summary."""
        # Arrange
        test_date = date.today()
        stock_code = "2317"
        
        mock_summary_data = [
            {'stock_code': stock_code, 'stock_name': 'Hon Hai', 'date': test_date.replace(day=15), 'open_price': 100.0, 'close_price': 102.0, 'high_price': 103.0, 'low_price': 99.0, 'volume': 12000}
        ]
        mock_summary = MonthlySummary(
            stock_code=stock_code,
            month="2025-09", # Example month
            data=mock_summary_data
        )

        mock_generate_monthly_summary.return_value = mock_summary
        sys.argv = ['main.py', '--stocks', stock_code, '--monthly']
        
        # Act
        main.main()
        
        # Assert
        output = self.captured_output.getvalue()
        self.assertIn("--- Monthly Summary", output)
        self.assertIn(stock_code, output)
        self.assertIn("Hon Hai", output)
        self.assertIn("102.0", output) # Check for close price
        mock_db_service.initialize_db.assert_called_once()
        mock_generate_monthly_summary.assert_called_once_with(stock_code, test_date)

    @patch('src.cli.main.summary_service.display_date_range_data')
    @patch('src.cli.main.db_service')
    def test_date_range_query_args(self, mock_db_service, mock_display_data):
        """Test argument parsing for date range queries."""
        # Arrange
        stock_code = "2330"
        start_date_str = "2025-09-01"
        end_date_str = "2025-09-05"
        
        sys.argv = ['main.py', '--stocks', stock_code, '--start-date', start_date_str, '--end-date', end_date_str]
        
        # Act
        main.main()
        
        # Assert
        mock_db_service.initialize_db.assert_called_once()
        mock_display_data.assert_called_once_with(
            stock_code=stock_code,
            start_date=datetime.strptime(start_date_str, "%Y-%m-%d").date(),
            end_date=datetime.strptime(end_date_str, "%Y-%m-%d").date()
        )

    @patch('src.cli.main.db_service')
    def test_invalid_date_format_handling(self, mock_db_service):
        """Test that an invalid date format exits and prints an error."""
        # Arrange
        sys.argv = ['main.py', '--stocks', '2330', '--start-date', '2025-9-1', '--end-date', '2025-09-05']
        
        # Act & Assert
        with self.assertRaises(SystemExit):
            main.main()
            
        # Assert error message
        self.assertIn("Invalid date format", self.captured_stderr.getvalue())
        mock_db_service.initialize_db.assert_called_once()

    @patch('src.cli.main.db_service')
    def test_start_date_after_end_date_handling(self, mock_db_service):
        """Test that a start date after end date exits and prints an error."""
        # Arrange
        sys.argv = ['main.py', '--stocks', '2330', '--start-date', '2025-09-05', '--end-date', '2025-09-01']
        
        # Act & Assert
        with self.assertRaises(SystemExit):
            main.main()
            
        # Assert error message
        self.assertIn("Start date cannot be after end date", self.captured_stderr.getvalue())
        mock_db_service.initialize_db.assert_called_once()

    @patch('src.cli.main.summary_service.display_date_range_data')
    @patch('src.cli.main.db_service')
    def test_default_end_date_handling(self, mock_db_service, mock_display_data):
        """Test that when --end-date is omitted, it defaults to today's date."""
        # Arrange
        stock_code = "2330"
        start_date_str = "2025-09-01"
        
        sys.argv = ['main.py', '--stocks', stock_code, '--start-date', start_date_str]
        
        # Act
        main.main()
        
        # Assert
        mock_db_service.initialize_db.assert_called_once()
        mock_display_data.assert_called_once_with(
            stock_code=stock_code,
            start_date=datetime.strptime(start_date_str, "%Y-%m-%d").date(),
            end_date=date.today() # Expect today's date as default
        )

    @patch('src.cli.main.data_fetcher.fetch_stock_data_in_range', return_value=[])
    @patch('src.cli.main.db_service')
    def test_invalid_stock_code_handling(self, mock_db_service, mock_fetch):
        """Test that an invalid stock code prints a 'No data found' message."""
        # Arrange
        stock_code = 'INVALID'
        start_date = '2025-09-01'
        sys.argv = ['main.py', '--stocks', stock_code, '--start-date', start_date]

        # Act
        main.main()

        # Assert
        output = self.captured_output.getvalue()
        self.assertIn(f"No data found for the specified date range.", output)
        mock_db_service.initialize_db.assert_called_once()

    @patch('src.cli.main.summary_service.display_date_range_data')
    @patch('src.cli.main.db_service')
    def test_date_range_query_multiple_stocks(self, mock_db_service, mock_display_data):
        """Test date range queries for multiple stock codes."""
        # Arrange
        stock_codes = "2330,8086"
        start_date_str = "2025-09-01"
        end_date_str = "2025-09-05"
        
        sys.argv = ['main.py', '--stocks', stock_codes, '--start-date', start_date_str, '--end-date', end_date_str]
        
        # Act
        main.main()
        
        # Assert
        mock_db_service.initialize_db.assert_called_once()
        
        # Verify that display_date_range_data was called for each stock code
        calls = mock_display_data.call_args_list
        self.assertEqual(len(calls), 2)
        
        expected_start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        expected_end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        
        # Check the call for the first stock code
        calls[0].assert_called_with(
            stock_code='2330',
            start_date=expected_start_date,
            end_date=expected_end_date
        )
        
        # Check the call for the second stock code
        calls[1].assert_called_with(
            stock_code='8086',
            start_date=expected_start_date,
            end_date=expected_end_date
        )

    def test_end_to_end_query(self):
        """A full end-to-end test that queries real data."""
        # Arrange
        stock_code = "2330"
        start_date_str = "2024-01-02"
        end_date_str = "2024-01-03"

        # This is a real end-to-end test, so we don't mock services.
        # Ensure the database is clean before running.
        if os.path.exists("stock_data.db"):
            os.remove("stock_data.db")
        db_service.initialize_db()
        # You might want to clear the specific table if needed, e.g.,
        # with db_service.get_connection() as conn:
        #     conn.execute("DELETE FROM transaction_data WHERE stock_code = ?", (stock_code,))

        # We need to ensure some data exists for the query to return something.
        # Let's fetch it directly first.
        data_fetcher.fetch_stock_data_in_range(
            stock_code, 
            datetime.strptime(start_date_str, "%Y-%m-%d").date(),
            datetime.strptime(end_date_str, "%Y-%m-%d").date()
        )

        sys.argv = ['main.py', '--stock', stock_code, '--start-date', start_date_str, '--end-date', end_date_str]

        # Act
        main.main()

        # Assert
        output = self.captured_output.getvalue()
        self.assertIn(f"--- Transaction Data for {stock_code} from {start_date_str} to {end_date_str} ---", output)
        # We expect to see some data rows. The exact values depend on the `twstock` library.
        self.assertIn("open_price", output)
        self.assertIn("close_price", output)
        self.assertIn("Taiwan Semiconductor", output)

if __name__ == '__main__':
    unittest.main()
