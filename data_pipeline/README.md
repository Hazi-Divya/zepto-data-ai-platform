# Module 1 — Web Scraping, Cleaning, SQLite & Pandas Analysis

## Overview

This module builds an end-to-end data pipeline using the **Books to Scrape** website.

The pipeline performs:

1. Web scraping using `requests` and `BeautifulSoup`
2. Data cleaning and type conversion using Pandas
3. GBP to INR conversion using the fixed rate `1 GBP = 105.50 INR`
4. Normalized SQLite database creation
5. SQL analysis using multiple query types
6. SQL result analysis using `pandas.read_sql()`
7. Reproduction of a SQL `JOIN` using `pandas.merge()`
8. End-to-end execution without manual copy/paste

The complete pipeline can be executed using:

```bash
python data_pipeline/run_pipeline.py
```

---

## Data Source

The data is scraped from **Books to Scrape**, a website specifically designed for web-scraping practice.

- **Website:** https://books.toscrape.com/
- **Method:** Python `requests` + `BeautifulSoup`
- **Scraping approach:** Category pages with pagination
- **Minimum requirement:** At least 60 books from at least 3 categories
- **Final dataset:** 69 books from 3 categories

### Fields Collected

- `title`
- `price_gbp`
- `rating`
- `availability`
- `category`

The scraper automatically discovers book categories and follows pagination until the required number of books and categories is collected.

---

## Project Structure

```text
data_pipeline/
├── scraper.py
├── cleaner.py
├── database.py
├── queries.py
├── pandas_analysis.py
├── run_pipeline.py
├── README.md
│
├── data/
│   ├── raw_books.csv
│   └── cleaned_books.csv
│
├── database/
│   └── zepto_books.db
│
└── outputs/
    ├── sql_results.txt
    └── pandas_comparison.csv
```

---

## Web Scraping

The web scraping module uses Python `requests` and `BeautifulSoup` to collect book information from **Books to Scrape**.

### Scraping Process

1. The scraper connects to the Books to Scrape website using `requests`.
2. It automatically discovers available book categories.
3. It visits category pages and follows pagination using the **Next** link.
4. From each book card, it extracts:
   - Book title
   - Listed price in GBP
   - Star rating text
   - Availability text
   - Category
5. The scraper continues until at least **60 books** from at least **3 categories** are collected.
6. The raw scraped data is saved to `data/raw_books.csv`.

### Scraping Result

- **Total books scraped:** 69
- **Total categories:** 3
- **Raw output:** `data/raw_books.csv`

The scraper is designed to handle HTTP requests with a timeout and to follow pagination automatically without manual data collection.

---

## Data Cleaning

The scraped data is cleaned and validated using Python and Pandas before storing it in the database.

### Cleaning Process

1. Remove the currency symbols (`£` and `Â£`) from price values.
2. Convert `price_gbp` from text to `float`.
3. Convert star rating text to numeric values:
   - `One` → `1`
   - `Two` → `2`
   - `Three` → `3`
   - `Four` → `4`
   - `Five` → `5`
4. Convert availability text into a Boolean value:
   - `In stock` → `True`
   - `Out of stock` → `False`
5. Handle parsing failures:
   - Numeric parsing failures are replaced using the median value.
   - Rows with invalid availability, title, or category values are removed.
6. Calculate `price_inr` using the fixed conversion rate:
   - **1 GBP = 105.50 INR**
7. Validate the final dataset for:
   - Correct data types
   - Missing values
   - Valid ratings
   - Required row count
   - Required number of categories
8. Save the cleaned dataset to `data/cleaned_books.csv`.

### Cleaning Result

- **Total cleaned books:** 69
- **Categories:** 3
- `price_gbp`: `float`
- `price_inr`: `float`
- `rating`: `integer`
- `in_stock`: `boolean`
- **Missing values:** None in the final dataset

---

## GBP to INR Conversion

A fixed conversion rate is used throughout the project as required.

- **Conversion rate:** `1 GBP = 105.50 INR`
- The exchange rate is **fixed** and is not obtained from an external API.

The INR price is calculated using:

```text
price_inr = price_gbp × 105.50
```

### Example

```text
£10.00 × 105.50 = ₹1,055.00
```

---

## SQLite Database

The cleaned book data is stored in a normalized **SQLite database** named `zepto_books.db`.

### Database Schema

The database contains two related tables.

#### `categories`

| Column | Description |
|---|---|
| `category_id` | Primary Key |
| `category_name` | Unique category name |

#### `books`

| Column | Description |
|---|---|
| `book_id` | Primary Key |
| `title` | Book title |
| `price_gbp` | Book price in GBP |
| `price_inr` | Book price in INR |
| `rating` | Numeric rating from 1 to 5 |
| `in_stock` | Availability status |
| `category_id` | Foreign Key referencing `categories(category_id)` |

The `categories` and `books` tables are connected using `category_id`. This avoids storing the category name repeatedly for every book.

### Database Relationship

```text
categories
    │
    │ 1
    │
    │
    │ N
books
```

This represents a **one-to-many relationship**:

- One category can contain many books.
- Each book belongs to one category.

### Database Validation

- **Categories:** 3
- **Books:** 69
- **Orphaned books:** 0
- **Foreign key validation:** Passed

The database is recreated automatically during the pipeline run, so the complete process can be executed without manual data insertion.

### Database File

```text
database/zepto_books.db
```

---

## SQL Analysis

Seven SQL queries were created and executed on the SQLite database to demonstrate filtering, sorting, limiting, distinct values, range conditions, category selection, and table joins.

### Queries Performed

1. **SELECT and WHERE**  
   Retrieves books that are in stock and have a price greater than £20.

2. **ORDER BY**  
   Sorts books by price.

3. **ORDER BY with LIMIT**  
   Retrieves the top 10 most expensive books.

4. **DISTINCT**  
   Retrieves the unique book categories.

5. **BETWEEN**  
   Retrieves books with ratings between 4 and 5.

6. **IN**  
   Retrieves books belonging to selected categories.

7. **INNER JOIN**  
   Combines the `books` and `categories` tables using `category_id`.

The SQL queries and their printed outputs are saved in:

```text
outputs/sql_results.txt
```

All **7 SQL queries executed successfully**.

---

## Pandas Analysis

Pandas is used to read SQL query results from the SQLite database and perform the required in-memory analysis.

### Analysis Process

1. Read the `books` and `categories` tables from SQLite using `pd.read_sql()`.
2. Execute SQL queries and load at least two query results into Pandas DataFrames.
3. Reproduce the database `JOIN` operation using `pd.merge()` without using a SQL `JOIN`.
4. Compare the SQL `JOIN` result with the Pandas `merge()` result.
5. Verify that both results are equivalent.
6. Save the comparison result to:

```text
outputs/pandas_comparison.csv
```

### Result

- SQL results successfully loaded into Pandas.
- `JOIN` successfully reproduced using `pd.merge()`.
- SQL and Pandas results were equivalent.
- Comparison output saved successfully.

---

## End-to-End Pipeline

The complete data pipeline is automated through `run_pipeline.py`, so all stages can be executed without manual data copying or intervention.

### Pipeline Flow

```text
Books to Scrape
       │
       ▼
   Web Scraping
(requests + BeautifulSoup)
       │
       ▼
  Raw CSV Dataset
       │
       ▼
 Data Cleaning
     (Pandas)
       │
       ▼
 Cleaned CSV Dataset
       │
       ▼
 Normalized SQLite
    Database
       │
       ▼
    SQL Analysis
       │
       ▼
   Pandas Analysis
       │
       ▼
   Final Outputs
```

### Pipeline Steps

1. **Scraping** — Collects book data from Books to Scrape.
2. **Cleaning** — Cleans the scraped data, converts data types, handles parsing failures, and calculates INR prices.
3. **Database Creation** — Creates the normalized SQLite database and inserts the cleaned data.
4. **SQL Analysis** — Executes the required SQL queries and saves their outputs.
5. **Pandas Analysis** — Reads SQL results using Pandas and reproduces the SQL `JOIN` using `pd.merge()`.

---

## Installation

From the project root:

```bash
pip install -r data_pipeline/requirements.txt
```
### Run the Complete Pipeline

From the project root:

```bash
python data_pipeline/run_pipeline.py
```

---

## Final Verification

The pipeline successfully completed all stages with:

- **69 books**
- **3 categories**
- Correct data types
- **69 database records**
- **0 orphaned records**
- Foreign key validation passed
- **7 SQL queries executed successfully**
- SQL `JOIN` reproduced using Pandas
- SQL and Pandas results verified as equivalent
- Complete process runs automatically from scraping to analysis
- No manual copy/paste required

---

## Output Files

The data pipeline generates the following output files.

### Data Files

- `data/raw_books.csv` — Contains the raw book data collected from Books to Scrape.
- `data/cleaned_books.csv` — Contains the cleaned and validated book data with GBP and INR prices.

### Database

- `database/zepto_books.db` — SQLite database containing the normalized `categories` and `books` tables.

### Analysis Outputs

- `outputs/sql_results.txt` — Contains the SQL queries and their printed execution results.
- `outputs/pandas_comparison.csv` — Contains the comparison between the SQL `JOIN` result and the Pandas `pd.merge()` result.

These files are generated automatically when the end-to-end pipeline is executed.

---

## Design Decisions

The following design decisions were made to keep the data pipeline reliable, automated, and aligned with the project requirements.

- **Category-based scraping:** Categories and pagination are discovered automatically so the scraper can collect at least 60 books from at least 3 categories without manual selection.
- **Requests + BeautifulSoup:** These libraries are used for simple and reliable HTML page fetching and parsing.
- **Parsing failure handling:** Numeric parsing failures are handled using median imputation, while rows with invalid availability, title, or category values are dropped.
- **Fixed currency conversion:** A fixed rate of `1 GBP = 105.50 INR` is used instead of an external currency API, as required.
- **Normalized SQLite database:** Separate `categories` and `books` tables reduce data duplication and maintain relationships using primary and foreign keys.
- **Foreign key validation:** SQLite foreign key constraints and validation checks are used to prevent orphaned book records.
- **SQL + Pandas analysis:** SQL is used for database-level analysis, while Pandas is used for in-memory analysis and to reproduce the SQL `JOIN` using `pd.merge()`.
- **Automated execution:** `run_pipeline.py` connects all stages so the entire workflow can be executed with a single command.
- **Reproducible outputs:** Raw data, cleaned data, database files, SQL results, and Pandas comparison results are saved as project outputs for verification.

---

## Verification Summary

The completed data pipeline was verified against the project requirements.

| Check | Result |
|---|---|
| Books scraped | **69** |
| Categories | **3** |
| Cleaned records | **69** |
| GBP → INR conversion | **1 GBP = 105.50 INR** |
| SQLite categories | **3** |
| SQLite books | **69** |
| Orphaned records | **0** |
| Foreign key validation | **Passed** |
| SQL queries executed | **7** |
| Pandas SQL results | **Successfully loaded** |
| Pandas `JOIN` using `pd.merge()` | **Completed** |
| SQL vs Pandas `JOIN` | **Equivalent** |
| End-to-end pipeline | **Completed successfully** |
| Manual copy/paste required | **No** |

---

## Conclusion

Module 1 implements a complete automated data pipeline covering:

**Web Scraping → Data Cleaning → Currency Conversion → SQLite Database → SQL Analysis → Pandas Analysis**

All major Module 1 requirements were completed and verified through the automated end-to-end pipeline.
