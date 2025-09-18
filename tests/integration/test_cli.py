import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from datetime import date

from src.cli import main
from src.models.stock_data import TransactionData

class TestCli(unittest.TestCase):

    @patch('src.cli.main.data_fetcher')
    @patch('src.cli.main.db_service')
    def test_daily_data_display(self, mock_db_service, mock_data_fetcher):
        """Test the CLI for displaying daily stock data."""
        # Arrange
        test_date = date.today()
        stock_code = "2330"
        
        # Mock the data fetcher to return some data
        mock_data = TransactionData(
            stock_code=stock_code, date=test_date, open_price=900.0, 
            close_price=905.0, high_price=910.0, low_price=899.0, volume=50000
        )
        mock_data_fetcher.fetch_stock_data.return_value = [mock_data]
        
        # Redirect stdout to capture the print output
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Mock sys.argv
        sys.argv = ['main.py', '--stocks', stock_code]
        
        # Act
        main.main()
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Assert
        output = captured_output.getvalue()
        self.assertIn("--- Daily Transaction Data", output)
        self.assertIn(stock_code, output)
        self.assertIn("905.0", output) # Check for close price
        self.assertIn("50000", output) # Check for volume
        
        # Assert that the db was initialized
        mock_db_service.initialize_db.assert_called_once()

if __name__ == '__main__':
    unittest.main()
