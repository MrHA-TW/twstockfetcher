# Research: Taiwan Stock Market Transaction Data Tool

## Python Libraries for Web Scraping and Data Manipulation

*   **twstock**: A Python library specifically for fetching Taiwan stock data. This seems to be the most direct and easiest way to get the data.
*   **requests**: For making HTTP requests to fetch the web page content. This might be needed if `twstock` doesn't provide all the necessary data.
*   **beautifulsoup4**: For parsing HTML and XML documents. This might be needed if `twstock` doesn't provide all the necessary data.
*   **pandas**: For data manipulation and analysis, and for displaying data in a tabular format.

**Decision**: Use `twstock` as the primary library for fetching data. Use `pandas` for data manipulation and display. `requests` and `beautifulsoup4` will be used as fallbacks if `twstock` is insufficient.

**Rationale**: `twstock` is a specialized library for Taiwan stock data, which should be more reliable and easier to use than general-purpose web scraping libraries. `pandas` is the standard for data manipulation in Python.

**Alternatives considered**: `scrapy` (a full-fledged web scraping framework, which is an overkill for this project), `lxml` (another HTML/XML parser, but `beautifulsoup4` is more beginner-friendly).
