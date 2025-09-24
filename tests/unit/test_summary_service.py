import unittest
from unittest.mock import patch
from datetime import date, timedelta
from io import StringIO

from src.services import summary_service
from src.models.stock_data import TransactionData, WeeklySummary, MonthlySummary

class TestSummaryService(unittest.TestCase):

    @patch('src.services.summary_service.data_fetcher')
    def test_generate_weekly_summary(self, mock_data_fetcher):
        """Test the weekly summary generation logic with mock data."""
        # Arrange
        today = date(2025, 9, 20)  # A Saturday
        stock_code = "2330"

        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=4)

        # Mock the data that data_fetcher.fetch_stock_data would return
        mock_data = [
            TransactionData(
                '2330', today - timedelta(days=2), 900, 905, 910, 899, 100
            ),  # Thursday
            TransactionData(
                '2330', today - timedelta(days=1), 906, 910, 915, 905, 120
            ),  # Friday
        ]

        # This mock will return data for the days we have it, and None otherwise
        def side_effect(code, dt):
            for d in mock_data:
                if d.date == dt and d.stock_code == code:
                    return [d]
            return []

        mock_data_fetcher.fetch_stock_data.side_effect = side_effect

        # Act
        summary = summary_service.generate_weekly_summary(stock_code, today)

        # Assert
        self.assertIsInstance(summary, WeeklySummary)
        self.assertEqual(summary.stock_code, stock_code)
        self.assertEqual(summary.start_date, start_of_week)
        self.assertEqual(summary.end_date, end_of_week)
        self.assertEqual(len(summary.data), 2)
        self.assertEqual(summary.data[0].close_price, 905)
        self.assertEqual(mock_data_fetcher.fetch_stock_data.call_count, 5)

    @patch('src.services.summary_service.data_fetcher')
    def test_generate_monthly_summary(self, mock_data_fetcher):
        """Test the monthly summary generation logic for the previous month."""
        # Arrange
        today = date(2025, 10, 1) # First day of October
        stock_code = "2317"
        
        # Mock data for September 2025
        mock_data = [
            TransactionData('2317', date(2025, 9, 15), 100, 102, 103, 99, 200),
            TransactionData('2317', date(2025, 9, 30), 105, 108, 110, 104, 250),
        ]

        def side_effect(code, dt):
            for d in mock_data:
                if d.date == dt and d.stock_code == code:
                    return [d]
            return []

        mock_data_fetcher.fetch_stock_data.side_effect = side_effect

        # Act
        summary = summary_service.generate_monthly_summary(stock_code, today)

        # Assert
        self.assertIsInstance(summary, MonthlySummary)
        self.assertEqual(summary.stock_code, stock_code)
        self.assertEqual(summary.month, "2025-09")
        self.assertEqual(len(summary.data), 2)
        self.assertEqual(summary.data[1].close_price, 108)
        # calendar.monthrange(2025, 9) is (1, 30), so it should be called 30 times
        self.assertEqual(mock_data_fetcher.fetch_stock_data.call_count, 30)

    @patch('src.services.summary_service.data_fetcher')
    @patch('sys.stdout', new_callable=StringIO)
    def test_display_date_range_data(self, mock_stdout, mock_data_fetcher):
        """Test the display of date range data."""
        # Arrange
        stock_code = "2330"
        start_date = date(2025, 9, 1)
        end_date = date(2025, 9, 2)
        mock_data = [
            TransactionData('2330', start_date, 900, 905, 910, 899, 10000),
            TransactionData('2330', end_date, 906, 910, 915, 905, 12000),
        ]
        mock_data_fetcher.fetch_stock_data_in_range.return_value = mock_data

        # Act
        summary_service.display_date_range_data(stock_code, start_date, end_date)

        # Assert
        output = mock_stdout.getvalue()
        self.assertIn(f"--- Transaction Data for {stock_code} from {start_date} to {end_date} ---", output)
        self.assertIn("905", output) # Check for close price
        self.assertIn("12000", output) # Check for volume

    @patch('src.services.summary_service.data_fetcher')
    @patch('sys.stdout', new_callable=StringIO)
    def test_display_date_range_data_no_data(self, mock_stdout, mock_data_fetcher):
        """Test the display of date range data when no data is found."""
        # Arrange
        stock_code = "2330"
        start_date = date(2025, 9, 1)
        end_date = date(2025, 9, 2)
        mock_data_fetcher.fetch_stock_data_in_range.return_value = []

        # Act
        summary_service.display_date_range_data(stock_code, start_date, end_date)

        # Assert
        output = mock_stdout.getvalue()
        self.assertIn("No data found for the specified date range.", output)

if __name__ == '__main__':
    unittest.main()
