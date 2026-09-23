from pathlib import Path
import sqlite3

import pandas as pd


BASE_DIR = Path(__file__).parent
DB_FILE = BASE_DIR / "database" / "zepto_books.db"
OUTPUT_FILE = BASE_DIR / "outputs" / "pandas_comparison.csv"


def main():
    conn = sqlite3.connect(DB_FILE)

    # ---------------------------------------------------------
    # 1. Read SQL query results using pd.read_sql()
    # ---------------------------------------------------------

    query_1 = """
        SELECT title, price_gbp, rating
        FROM books
        WHERE rating >= 4
        ORDER BY price_gbp DESC
        LIMIT 10
    """

    query_7 = """
        SELECT
            b.book_id,
            b.title,
            b.price_gbp,
            b.price_inr,
            b.rating,
            b.in_stock,
            c.category_name
        FROM books b
        INNER JOIN categories c
            ON b.category_id = c.category_id
        ORDER BY b.price_gbp DESC
        LIMIT 20
    """

    sql_result_1 = pd.read_sql(query_1, conn)
    sql_join_result = pd.read_sql(query_7, conn)

    print("\n--- Query 1 loaded with pd.read_sql() ---")
    print(sql_result_1)

    print("\n--- SQL JOIN result loaded with pd.read_sql() ---")
    print(sql_join_result)

    # ---------------------------------------------------------
    # 2. Load the two tables into Pandas DataFrames
    # ---------------------------------------------------------

    books_df = pd.read_sql(
        """
        SELECT
            book_id,
            title,
            price_gbp,
            price_inr,
            rating,
            in_stock,
            category_id
        FROM books
        """,
        conn,
    )

    categories_df = pd.read_sql(
        """
        SELECT category_id, category_name
        FROM categories
        """,
        conn,
    )

    conn.close()

    # ---------------------------------------------------------
    # 3. Reproduce the SQL JOIN using pd.merge()
    # ---------------------------------------------------------

    pandas_join_result = pd.merge(
        books_df,
        categories_df,
        on="category_id",
        how="inner",
    )

    # Select the same columns and ordering as the SQL query
    pandas_join_result = pandas_join_result[
        [
            "book_id",
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category_name",
        ]
    ].sort_values(
        by="price_gbp",
        ascending=False
    ).head(20).reset_index(drop=True)

    sql_join_result = sql_join_result.reset_index(drop=True)

    # ---------------------------------------------------------
    # 4. Compare SQL JOIN and Pandas merge()
    # ---------------------------------------------------------

    equivalent = sql_join_result.equals(pandas_join_result)

    print("\n--- SQL JOIN vs Pandas merge() ---")

    comparison = pd.DataFrame(
        {
            "SQL JOIN": sql_join_result["title"],
            "Pandas merge()": pandas_join_result["title"],
        }
    )

    print(comparison)

    print(f"\nResults equivalent: {equivalent}")

    # ---------------------------------------------------------
    # 5. Save side-by-side comparison
    # ---------------------------------------------------------

    comparison.to_csv(OUTPUT_FILE, index=False)

    print(f"\nComparison saved to:")
    print(OUTPUT_FILE)

    if not equivalent:
        raise AssertionError(
            "SQL JOIN and Pandas merge() results are not equivalent."
        )

    print("\nPandas SQL analysis completed successfully.")


if __name__ == "__main__":
    main()