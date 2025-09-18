# Development Tasks: Taiwan Stock Market Transaction Data Tool

This file outlines the tasks required to implement the Taiwan Stock Market Transaction Data Tool, based on the [spec.md](./spec.md) and [plan.md](./plan.md).

## Phase 1: Project Setup & Core Data Services

-   [ ] **Task 1.1: Initialize Project Structure**:
    -   Create the directory structure as defined in `plan.md`: `src/models`, `src/services`, `src/cli`, `src/lib`, `tests/contract`, `tests/integration`, `tests/unit`.
    -   Add `__init__.py` files to the necessary directories to make them Python packages.

-   [ ] **Task 1.2: Define Data Models**:
    -   Create `src/models/stock_data.py`.
    -   Implement the `Stock`, `TransactionData`, `WeeklySummary`, and `MonthlySummary` data classes as defined in `data-model.md`.

-   [ ] **Task 1.3: Setup Database Service**:
    -   Create `src/services/db_service.py`.
    -   Implement functions to initialize a SQLite database and create a table for `TransactionData`.
    -   Implement functions for `save_transaction_data` and `get_transaction_data_by_date`.

-   [ ] **Task 1.4: Implement Data Fetching & Caching Service**:
    -   Create `src/services/data_fetcher.py`.
    -   Implement a function `fetch_stock_data(stock_codes: list[str], date: date)`.
    -   This function should first query the local SQLite database via `db_service`.
    -   If data for the given stock and date exists, return it.
    -   If not, use the `twstock` library to fetch the data.
    -   After fetching, save the new data to the database using `db_service`.
    -   Return a list of `TransactionData` objects.
    -   Include error handling for invalid stock codes or network issues.

-   [ ] **Task 1.5: Write Integration Tests for Services**:
    -   Create `tests/integration/test_db_service.py` to test database operations.
    -   Create `tests/integration/test_data_fetcher.py`.
    -   Write tests to verify that `fetch_stock_data` correctly fetches data and stores it.
    -   Write tests to verify that the service retrieves data from the cache (database) on subsequent calls.

## Phase 2: Command-Line Interface (CLI)

-   [ ] **Task 2.1: Implement Basic CLI**:
    -   Create `src/cli/main.py`.
    -   Use `argparse` to implement the command-line arguments: `--stocks` (required) and optional flags `--weekly`, `--monthly`.
    -   The CLI should call the `fetch_stock_data` service.

-   [ ] **Task 2.2: Implement Daily Data Display**:
    -   In `src/cli/main.py`, when no flags are present, format the fetched `TransactionData` into a `pandas` DataFrame and print it to the console.
    -   The table should be clear and readable.

-   [ ] **Task 2.3: Write E2E Tests for Daily Data CLI**:
    -   Create `tests/integration/test_cli.py`.
    -   Write a test that runs the CLI with a stock code and verifies that the output contains expected data points (e.g., stock code, price headers).

## Phase 3: Summary Logic and Implementation

-   [ ] **Task 3.1: Implement Weekly Summary Logic**:
    -   Create `src/services/summary_service.py`.
    -   Implement a function `generate_weekly_summary(data: list[TransactionData])` that processes a list of transaction data and returns a `WeeklySummary` object.
    -   The logic should correctly identify the past week's data.

-   [ ] **Task 3.2: Implement Monthly Summary Logic**:
    -   In `src/services/summary_service.py`, implement `generate_monthly_summary(data: list[TransactionData])` that returns a `MonthlySummary` object.

-   [ ] **Task 3.3: Integrate Summary Logic into CLI**:
    -   In `src/cli/main.py`, add logic to call the appropriate summary service function when `--weekly` or `--monthly` flags are used.
    -   Display the summary data in a user-friendly format.

-   [ ] **Task 3.4: Write Unit Tests for Summary Logic**:
    -   Create `tests/unit/test_summary_service.py`.
    -   Write unit tests to verify the correctness of the weekly and monthly summary generation logic using mock data.

## Phase 4: Finalization

-   [ ] **Task 4.1: Add Quickstart Documentation**:
    -   Update `quickstart.md` with final, verified commands and examples.

-   [ ] **Task 4.2: Code Refinement and Review**:
    -   Review all code for clarity, comments, and adherence to the plan.
    -   Ensure all tests are passing.