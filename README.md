# Stock Fetcher

This is a command-line tool to fetch stock data for both listed (TWSE) and over-the-counter (TPEx) stocks in Taiwan.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/MrHA-TW/twstockfetcher.git
    cd twstockfetcher
    ```

2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

All commands will automatically fetch and cache the required stock data.

### Querying by Date Range

To query stock data for a specific date range, use the `--stocks`, `--start-date`, and `--end-date` arguments. The stock name is now included in the output.

```bash
# Query a listed stock (e.g., TSMC)
python3 -m src.cli.main --stocks 2330 --start-date 2024-01-02 --end-date 2024-01-03
```

**Example Output:**

```
--- Transaction Data for 2330 from 2024-01-02 to 2024-01-03 ---
 stock_code                                         stock_name       date  open_price  high_price  low_price  close_price   volume
       2330 Taiwan Semiconductor Manufacturing Company Limited 2024-01-02       590.0       593.0      589.0        593.0 26059058
       2330 Taiwan Semiconductor Manufacturing Company Limited 2024-01-03       584.0       585.0      576.0        578.0 37106763
```

If `--end-date` is omitted, it will default to the current date.

### Getting Stock Information

To get key investment metrics for a stock, use the `--info` flag:

```bash
python3 -m src.cli.main --stocks 2330 --info
```

**Example Output:**

```
--- Key Investment Metrics for 2330 ---
公司名稱:                Taiwan Semiconductor Manufacturing Company Limited
產業:                  Semiconductors
市值:                  36,305,660,542,976
本益比:                 25.139164
預期本益比:               24.250822
股價淨值比:               7.9251413
股息殖利率:               147.00%
Beta值:               1.216
目前股價:                1400.0
52週最高價:              1400.0
52週最低價:              780.0
```

### Daily Data

To get the daily data for one or more stocks, use the `--stocks` argument with a comma-separated list of stock codes:

```bash
python3 -m src.cli.main --stocks 2330,2317
```

**Example Output:**
```
--- Daily Transaction Data for 2025-10-01 ---
 stock_code                                         stock_name       date  open_price  high_price  low_price  close_price    volume
       2330 Taiwan Semiconductor Manufacturing Company Limited 2025-10-01       900.0       910.0      899.0        905.0  50000000
       2317                           Hon Hai Precision Industry Co. 2025-10-01       180.0       182.0      179.0        181.0  80000000
```

### Weekly and Monthly Summaries

To get a summary for the past week or month, use the `--weekly` or `--monthly` flags, along with the `--stocks` argument:

```bash
# Weekly summary
python3 -m src.cli.main --stocks 2330 --weekly
```

**Example Output:**
```
--- Weekly Summary for Week Ending 2025-10-01 ---

Stock: 2330 (2025-09-29 to 2025-10-03)
 stock_code                                         stock_name       date  open_price  high_price  low_price  close_price   volume
       2330 Taiwan Semiconductor Manufacturing Company Limited 2025-09-29       900.0       910.0      899.0        905.0  50000000
       2330 Taiwan Semiconductor Manufacturing Company Limited 2025-09-30       906.0       915.0      905.0        910.0  52000000
       2330 Taiwan Semiconductor Manufacturing Company Limited 2025-10-01       911.0       918.0      908.0        912.0  48000000
```