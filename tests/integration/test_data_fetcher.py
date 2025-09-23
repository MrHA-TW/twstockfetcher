import unittest
from unittest.mock import patch, MagicMock
from datetime import date, datetime

from src.models.stock_data import TransactionData
from src.services import data_fetcher

class TestDataFetcher(unittest.TestCase):

    @patch('src.services.data_fetcher.db_service')
    def test_01_fetch_from_cache(self, mock_db_service):
        """Test that data is returned from the database if it exists."""
        test_date = date(2025, 9, 18)
        stock_code = "2330"
        
        # Mock the database to return a cached entry
        mock_cached_data = TransactionData(
            stock_code=stock_code, date=test_date, open_price=900.0, 
            close_price=905.0, high_price=910.0, low_price=899.0, volume=50000
        )
        mock_db_service.get_transaction_data_by_date.return_value = mock_cached_data

        # Call the fetcher
        result = data_fetcher.fetch_stock_data(stock_code, test_date)

        # Assert that the db service was called
        mock_db_service.get_transaction_data_by_date.assert_called_once_with(stock_code, test_date)
        
        # Assert that the result is the cached data
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], mock_cached_data)

    @patch('src.services.data_fetcher.twstock')
    @patch('src.services.data_fetcher.db_service')
    def test_02_fetch_from_web_and_save(self, mock_db_service, mock_twstock):
        """Test that data is fetched from the web and saved if not in the database."""
        test_date = date(2025, 9, 19)
        stock_code = "2317"

        # Mock the database to return nothing
        mock_db_service.get_transaction_data_by_date.return_value = None

        # Mock the twstock API response
        mock_stock = MagicMock()
        mock_twstock.Stock.return_value = mock_stock
        
        # Create a mock data point that twstock would return
        mock_web_data = MagicMock()
        mock_web_data.date = datetime(2025, 9, 19)
        mock_web_data.open = 100.0
        mock_web_data.close = 102.0
        mock_web_data.high = 103.0
        mock_web_data.low = 99.0
        mock_web_data.capacity = 10000
        mock_stock.fetch.return_value = [mock_web_data]

        # Call the fetcher
        result = data_fetcher.fetch_stock_data(stock_code, test_date)

        # Assert that the db service was called to check for data
        mock_db_service.get_transaction_data_by_date.assert_called_once_with(stock_code, test_date)
        
        # Assert that twstock was called
        mock_twstock.Stock.assert_called_once_with(stock_code)
        mock_stock.fetch.assert_called_once_with(2025, 9)

        # Assert that the new data was saved to the db
        mock_db_service.save_transaction_data.assert_called_once()
        self.assertEqual(mock_db_service.save_transaction_data.call_args[0][0][0].stock_code, stock_code)

        # Assert that the result is the newly fetched data
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].close_price, 102.0)

    @patch('src.services.data_fetcher.twstock')
    @patch('src.services.data_fetcher.db_service')
    def test_fetch_data_for_date_range(self, mock_db_service, mock_twstock):
        """Test fetching data for a date range from the web and saving it."""
        stock_code = "2330"
        start_date = date(2025, 9, 1)
        end_date = date(2025, 9, 3)

        # Mock the database to return nothing for this range
        mock_db_service.get_transaction_data_by_range.return_value = []

        # Mock the twstock API response for September
        mock_stock = MagicMock()
        mock_twstock.Stock.return_value = mock_stock
        
        mock_web_data_1 = MagicMock()
        mock_web_data_1.date = datetime(2025, 9, 1)
        mock_web_data_1.open, mock_web_data_1.close, mock_web_data_1.high, mock_web_data_1.low, mock_web_data_1.capacity = (900, 905, 910, 899, 10000)
        
        mock_web_data_2 = MagicMock()
        mock_web_data_2.date = datetime(2025, 9, 2)
        mock_web_data_2.open, mock_web_data_2.close, mock_web_data_2.high, mock_web_data_2.low, mock_web_data_2.capacity = (906, 910, 915, 905, 12000)

        mock_web_data_3 = MagicMock()
        mock_web_data_3.date = datetime(2025, 9, 3)
        mock_web_data_3.open, mock_web_data_3.close, mock_web_data_3.high, mock_web_data_3.low, mock_web_data_3.capacity = (911, 908, 916, 907, 11000)

        mock_stock.fetch.return_value = [mock_web_data_1, mock_web_data_2, mock_web_data_3]

        # Call the new function
        result = data_fetcher.fetch_stock_data_in_range(stock_code, start_date, end_date)

        # Assertions
        mock_db_service.get_transaction_data_by_range.assert_called_once_with(stock_code, start_date, end_date)
        mock_twstock.Stock.assert_called_once_with(stock_code)
        mock_stock.fetch.assert_called_once_with(2025, 9)
        mock_db_service.save_transaction_data.assert_called_once()
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].date, start_date)
        self.assertEqual(result[2].date, end_date)
        self.assertEqual(result[1].close_price, 910)

if __name__ == '__main__':
    unittest.main()
