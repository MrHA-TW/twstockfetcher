import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from datetime import date, datetime

from src.cli import main
from src.models.stock_data import TransactionData

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
            stock_code=stock_code, date=test_date, open_price=900.0, 
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
        mock_db_service.initialize_db.assert_called_once()

    @patch('src.cli.main.summary_service.display_date_range_data')
    @patch('src.cli.main.db_service')
    def test_date_range_query_args(self, mock_db_service, mock_display_data):
        """Test argument parsing for date range queries."""
        # Arrange
        stock_code = "2330"
        start_date_str = "2025-09-01"
        end_date_str = "2025-09-05"
        
        sys.argv = ['main.py', '--stock', stock_code, '--start-date', start_date_str, '--end-date', end_date_str]
        
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
        sys.argv = ['main.py', '--stock', '2330', '--start-date', '2025-9-1', '--end-date', '2025-09-05']
        
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
        sys.argv = ['main.py', '--stock', '2330', '--start-date', '2025-09-05', '--end-date', '2025-09-01']
        
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
        
        sys.argv = ['main.py', '--stock', stock_code, '--start-date', start_date_str]
        
        # Act
        main.main()
        
        # Assert
        mock_db_service.initialize_db.assert_called_once()
        mock_display_data.assert_called_once_with(
            stock_code=stock_code,
            start_date=datetime.strptime(start_date_str, "%Y-%m-%d").date(),
            end_date=date.today() # Expect today's date as default
        )

if __name__ == '__main__':
    unittest.main()
