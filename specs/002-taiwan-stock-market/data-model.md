# Data Model: Taiwan Stock Market Transaction Data Tool

## Entities

### Stock
-   **stock_code**: string (e.g., "2330")
-   **stock_name**: string (e.g., "TSMC")

### TransactionData
-   **date**: date
-   **open_price**: float
-   **close_price**: float
-   **high_price**: float
-   **low_price**: float
-   **volume**: integer

### WeeklySummary
-   **start_date**: date
-   **end_date**: date
-   **data**: list of TransactionData

### MonthlySummary
-   **month**: string (e.g., "2025-09")
-   **data**: list of TransactionData
