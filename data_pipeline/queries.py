from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "database" / "zepto_books.db"
OUTPUT_FILE = BASE_DIR / "outputs" / "sql_results.txt"


QUERIES = {
    "Query 1 - In-stock books above £20": """
        SELECT
            title,
            price_gbp,
            rating,
            in_stock
        FROM books
        WHERE in_stock = 1
          AND price_gbp > 20
        ORDER BY price_gbp DESC;
    """,

    "Query 2 - Books ordered by price": """
        SELECT
            title,
            price_gbp,
            price_inr
        FROM books
        ORDER BY price_gbp DESC;
    """,

    "Query 3 - Top 10 most expensive books": """
        SELECT
            title,
            price_gbp,
            price_inr
        FROM books
        ORDER BY price_gbp DESC
        LIMIT 10;
    """,

    "Query 4 - Distinct categories": """
        SELECT DISTINCT
            category_name
        FROM categories
        ORDER BY category_name;
    """,

    "Query 5 - Books rated between 4 and 5": """
        SELECT
            title,
            rating,
            price_gbp
        FROM books
        WHERE rating BETWEEN 4 AND 5
        ORDER BY rating DESC, price_gbp DESC;
    """,

    "Query 6 - Books from selected categories": """
        SELECT
            title,
            category_id,
            rating
        FROM books
        WHERE category_id IN (
            SELECT category_id
            FROM categories
            WHERE category_name IN (
                'Academic',
                'Adult Fiction'
            )
        )
        ORDER BY rating DESC, title;
    """,

    "Query 7 - Books with category names using JOIN": """
        SELECT
            b.title,
            b.rating,
            b.price_gbp,
            b.price_inr,
            b.in_stock,
            c.category_name
        FROM books AS b
        INNER JOIN categories AS c
            ON b.category_id = c.category_id
        ORDER BY c.category_name, b.rating DESC, b.title
        LIMIT 20;
    """,
}


def run_query(
    connection: sqlite3.Connection,
    query: str,
):
    """Execute a SQL query and return column names and rows."""

    cursor = connection.execute(query)

    columns = [
        description[0]
        for description in cursor.description
    ]

    rows = cursor.fetchall()

    return columns, rows


def format_result(columns, rows) -> str:
    """Format query results as readable text."""

    lines = []

    lines.append(" | ".join(columns))
    lines.append("-" * 100)

    for row in rows:
        lines.append(
            " | ".join(str(value) for value in row)
        )

    return "\n".join(lines)


def main() -> None:
    """Execute all required SQL queries."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(DATABASE_FILE)

    try:
        output_sections = []

        for query_name, query in QUERIES.items():

            print("\n" + "=" * 80)
            print(query_name)
            print("=" * 80)

            print("\nSQL:")
            print(query.strip())

            columns, rows = run_query(
                connection,
                query,
            )

            formatted_result = format_result(
                columns,
                rows,
            )

            print("\nOutput:")
            print(formatted_result)

            output_sections.append(
                f"{'=' * 80}\n"
                f"{query_name}\n"
                f"{'=' * 80}\n\n"
                f"SQL:\n"
                f"{query.strip()}\n\n"
                f"Output:\n"
                f"{formatted_result}\n"
            )

        OUTPUT_FILE.write_text(
            "\n\n".join(output_sections),
            encoding="utf-8",
        )

    finally:
        connection.close()

    print(
        f"\nAll SQL queries completed successfully."
    )

    print(
        f"Results saved to:\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()