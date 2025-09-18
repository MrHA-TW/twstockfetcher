# Quickstart: Taiwan Stock Market Transaction Data Tool

## Setup

1.  Install Python 3.11.
2.  Install the required libraries:
    ```
    pip install twstock pandas
    ```

## Usage

### Get today's transaction data

```
python src/cli/main.py --stocks 2330,2317
```

### Get weekly summary

```
python src/cli/main.py --stocks 2330,2317 --weekly
```

### Get monthly summary

```
python src/cli/main.py --stocks 2330,2317 --monthly
```
