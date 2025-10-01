import unittest
from unittest.mock import patch, call
from datetime import date, timedelta
import pandas as pd

from src.models.stock_data import TransactionData
from src.services import data_fetcher

class TestDataFetcher(unittest.TestCase):

    @patch('src.services.data_fetcher.db_service')
    def test_01_fetch_from_cache(self, mock_db_service):
        """Test that data is returned from the database if it exists."""
        test_date = date(2025, 9, 18)
        stock_code = "2330"
        
        mock_cached_data = TransactionData(
            stock_code=stock_code, stock_name="TSMC", date=test_date, open_price=900.0, 
            close_price=905.0, high_price=910.0, low_price=899.0, volume=50000
        )
        mock_db_service.get_transaction_data_by_date.return_value = mock_cached_data

        result = data_fetcher.fetch_stock_data(stock_code, test_date)

        mock_db_service.get_transaction_data_by_date.assert_called_once_with(stock_code, test_date)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], mock_cached_data)

    @patch('src.services.data_fetcher._get_stock_name', return_value="Hon Hai Precision")
    @patch('src.services.data_fetcher.yf.download')
    @patch('src.services.data_fetcher.db_service')
    def test_02_fetch_listed_from_web_and_save(self, mock_db_service, mock_yf_download, mock_get_name):
        """Test fetching listed stock data from the web (first try success)."""
        test_date = date(2025, 9, 19)
        stock_code = "2317"

        mock_db_service.get_transaction_data_by_date.return_value = None

        mock_df = pd.DataFrame({
            'Open': [100.0], 'High': [103.0], 'Low': [99.0], 'Close': [102.0], 'Volume': [10000]
        }, index=pd.to_datetime([test_date]))
        mock_yf_download.return_value = mock_df

        result = data_fetcher.fetch_stock_data(stock_code, test_date)

        mock_db_service.get_transaction_data_by_date.assert_called_once_with(stock_code, test_date)
        mock_yf_download.assert_called_once_with(
            "2317.TW", start=test_date, end=test_date + timedelta(days=1), progress=False, auto_adjust=False
        )
        mock_db_service.save_transaction_data.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].close_price, 102.0)
        self.assertEqual(result[0].stock_name, "Hon Hai Precision")

    @patch('src.services.data_fetcher._get_stock_name', return_value="GlobalWafers")
    @patch('src.services.data_fetcher.yf.download')
    @patch('src.services.data_fetcher.db_service')
    def test_03_fetch_otc_from_web_and_save(self, mock_db_service, mock_yf_download, mock_get_name):
        """Test fetching OTC stock data (.TW fails, .TWO succeeds)."""
        test_date = date(2025, 9, 22)
        stock_code = "6488"

        mock_db_service.get_transaction_data_by_date.return_value = None

        # Mock yf.download to fail on .TW and succeed on .TWO
        mock_otc_df = pd.DataFrame({
            'Open': [500.0], 'High': [510.0], 'Low': [498.0], 'Close': [505.0], 'Volume': [5000]
        }, index=pd.to_datetime([test_date]))
        
        mock_yf_download.side_effect = [
            pd.DataFrame(), # Empty dataframe for the .TW call
            mock_otc_df      # Real dataframe for the .TWO call
        ]

        data_fetcher.fetch_stock_data(stock_code, test_date)

        # Check that download was called twice, first with .TW, then with .TWO
        calls = [
            call("6488.TW", start=test_date, end=test_date + timedelta(days=1), progress=False, auto_adjust=False),
            call("6488.TWO", start=test_date, end=test_date + timedelta(days=1), progress=False, auto_adjust=False)
        ]
        mock_yf_download.assert_has_calls(calls)
        self.assertEqual(mock_yf_download.call_count, 2)
        mock_db_service.save_transaction_data.assert_called_once()

    @patch('src.services.data_fetcher._get_stock_name', return_value="TSMC")
    @patch('src.services.data_fetcher.yf.download')
    @patch('src.services.data_fetcher.db_service')
    def test_04_fetch_data_for_date_range(self, mock_db_service, mock_yf_download, mock_get_name):
        """Test fetching data for a date range from the web."""
        stock_code = "2330"
        start_date = date(2025, 9, 1)
        end_date = date(2025, 9, 3)

        mock_db_service.get_transaction_data_by_range.side_effect = [
            [], 
            [ # Mock return for the final re-query
                TransactionData(stock_code, "TSMC", date(2025, 9, 1), 900, 905, 910, 899, 10000),
                TransactionData(stock_code, "TSMC", date(2025, 9, 2), 906, 910, 915, 905, 12000),
                TransactionData(stock_code, "TSMC", date(2025, 9, 3), 911, 908, 916, 907, 11000)
            ]
        ]

        dates = pd.to_datetime([date(2025, 9, 1), date(2025, 9, 2), date(2025, 9, 3)])
        mock_df = pd.DataFrame({
            'Open': [900, 906, 911], 'High': [910, 915, 916], 'Low': [899, 905, 907],
            'Close': [905, 910, 908], 'Volume': [10000, 12000, 11000]
        }, index=dates)
        mock_yf_download.return_value = mock_df

        result = data_fetcher.fetch_stock_data_in_range(stock_code, start_date, end_date)

        mock_yf_download.assert_called_once_with(
            "2330.TW", start=start_date, end=end_date + timedelta(days=1), progress=False, auto_adjust=False
        )
        mock_db_service.save_transaction_data.assert_called_once()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[1].close_price, 910)
        self.assertEqual(result[0].stock_name, "TSMC")

if __name__ == '__main__':
    unittest.main()
