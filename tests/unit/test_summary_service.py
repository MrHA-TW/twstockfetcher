import unittest
from unittest.mock import patch
from datetime import date, timedelta

from src.services import summary_service
from src.models.stock_data import TransactionData, WeeklySummary, MonthlySummary

class TestSummaryService(unittest.TestCase):

    @patch('src.services.summary_service.db_service')
    def test_generate_weekly_summary(self, mock_db_service):
        """Test the weekly summary generation logic with mock data."""
        # Arrange
        today = date(2025, 9, 20)  # A Saturday
        stock_code = "2330"

        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=4)

        # Mock the data that db_service.get_transaction_data_by_date would return
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
                    return d
            return None

        mock_db_service.get_transaction_data_by_date.side_effect = side_effect

        # Act
        summary = summary_service.generate_weekly_summary(stock_code, today)

        # Assert
        self.assertIsInstance(summary, WeeklySummary)
        self.assertEqual(summary.stock_code, stock_code)
        self.assertEqual(summary.start_date, start_of_week)
        self.assertEqual(summary.end_date, end_of_week)
        self.assertEqual(len(summary.data), 2)
        self.assertEqual(summary.data[0].close_price, 905)
        self.assertEqual(mock_db_service.get_transaction_data_by_date.call_count, 5)

    @patch('src.services.summary_service.db_service')
    def test_generate_monthly_summary(self, mock_db_service):
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
                    return d
            return None

        mock_db_service.get_transaction_data_by_date.side_effect = side_effect

        # Act
        summary = summary_service.generate_monthly_summary(stock_code, today)

        # Assert
        self.assertIsInstance(summary, MonthlySummary)
        self.assertEqual(summary.stock_code, stock_code)
        self.assertEqual(summary.month, "2025-09")
        self.assertEqual(len(summary.data), 2)
        self.assertEqual(summary.data[1].close_price, 108)
        # calendar.monthrange(2025, 9) is (1, 30), so it should be called 30 times
        self.assertEqual(mock_db_service.get_transaction_data_by_date.call_count, 30)

if __name__ == '__main__':
    unittest.main()
