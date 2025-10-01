import os
import sqlite3
import unittest
from datetime import date

from src.models.stock_data import TransactionData
from src.services import db_service

class TestDbService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a temporary test database before all tests."""
        cls.test_db_path = "test_stock_data.db"
        db_service.DB_PATH = cls.test_db_path
        # Ensure the db is clean before starting
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

    @classmethod
    def tearDownClass(cls):
        """Remove the test database after all tests are done."""
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

    def setUp(self):
        """Initialize the database before each test."""
        db_service.initialize_db()

    def tearDown(self):
        """Clean up the database by deleting the file after each test."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_01_initialize_db(self):
        """Test if the database and table are created successfully."""
        self.assertTrue(os.path.exists(self.test_db_path))
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transaction_data';")
        self.assertIsNotNone(cursor.fetchone())
        conn.close()

    def test_02_save_and_get_transaction_data(self):
        """Test saving a single transaction and retrieving it."""
        test_date = date(2025, 9, 18)
        mock_data = TransactionData(
            stock_code="2330",
            stock_name="TSMC",
            date=test_date,
            open_price=900.0,
            close_price=905.0,
            high_price=910.0,
            low_price=899.0,
            volume=50000
        )

        # Save data
        db_service.save_transaction_data([mock_data])

        # Retrieve data
        retrieved_data = db_service.get_transaction_data_by_date("2330", test_date)

        self.assertIsNotNone(retrieved_data)
        self.assertEqual(retrieved_data.stock_code, "2330")
        self.assertEqual(retrieved_data.stock_name, "TSMC")
        self.assertEqual(retrieved_data.date, test_date)

    def test_03_get_non_existent_data(self):
        """Test retrieving data that does not exist."""
        test_date = date(2025, 9, 19)
        retrieved_data = db_service.get_transaction_data_by_date("9999", test_date)
        self.assertIsNone(retrieved_data)

    def test_get_transaction_data_by_range(self):
        """Test retrieving transaction data for a date range."""
        start_date = date(2025, 9, 1)
        end_date = date(2025, 9, 3)
        mock_data = [
            TransactionData("2330", "TSMC", date(2025, 9, 1), 900, 905, 910, 899, 10000),
            TransactionData("2330", "TSMC", date(2025, 9, 2), 906, 910, 915, 905, 12000),
            TransactionData("2330", "TSMC", date(2025, 9, 3), 911, 908, 916, 907, 11000),
            TransactionData("2330", "TSMC", date(2025, 9, 4), 909, 912, 914, 908, 13000) # Out of range
        ]

        db_service.save_transaction_data(mock_data)

        # Retrieve data within the range
        retrieved_data = db_service.get_transaction_data_by_range("2330", start_date, end_date)

        self.assertIsNotNone(retrieved_data)
        self.assertEqual(len(retrieved_data), 3)
        self.assertEqual(retrieved_data[0].date, start_date)
        self.assertEqual(retrieved_data[2].date, end_date)
        self.assertEqual(retrieved_data[1].close_price, 910)

if __name__ == '__main__':
    unittest.main()
