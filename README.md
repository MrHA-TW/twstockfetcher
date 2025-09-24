# Stock Fetcher

This is a command-line tool to fetch stock data.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/MrHA-TW/twstockfetcher.git
    cd twstockfetcher
    ```

2.  Install the required dependencies:
    ```bash
    pip install pandas twstock
    ```

## Usage

### Querying by Date Range

To query stock data for a specific date range, use the `--stock`, `--start-date`, and `--end-date` arguments:

```bash
python3 -m src.cli.main --stock 2330 --start-date 2025-09-01 --end-date 2025-09-05
```

If `--end-date` is omitted, it will default to the current date.

### Daily Data

To get the daily data for one or more stocks, use the `--stocks` argument with a comma-separated list of stock codes:

```bash
python3 -m src.cli.main --stocks 2330,2317
```

### Weekly and Monthly Summaries

To get a summary for the past week or month, use the `--weekly` or `--monthly` flags, along with the `--stocks` argument:

```bash
# Weekly summary
python3 -m src.cli.main --stocks 2330,2317 --weekly

# Monthly summary
python3 -m src.cli.main --stocks 2330,2317 --monthly
```
