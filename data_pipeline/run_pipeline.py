from database import main as build_database
from cleaner import main as clean_data
from pandas_analysis import main as run_pandas_analysis
from queries import main as run_sql_queries
from scraper import main as scrape_data


def main():
    print("=" * 70)
    print("ZEPTO DATA PIPELINE - END-TO-END RUN")
    print("=" * 70)

    print("\n[1/5] Scraping books...")
    scrape_data()

    print("\n[2/5] Cleaning scraped data...")
    clean_data()

    print("\n[3/5] Creating SQLite database...")
    build_database()

    print("\n[4/5] Running SQL queries...")
    run_sql_queries()

    print("\n[5/5] Running Pandas SQL/merge analysis...")
    run_pandas_analysis()

    print("\n" + "=" * 70)
    print("END-TO-END PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()