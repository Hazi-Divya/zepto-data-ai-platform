from pathlib import Path
import sqlite3

import pandas as pd


# -------------------------------------------------------------------
# File paths
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

CLEANED_FILE = BASE_DIR / "data" / "cleaned_books.csv"
DATABASE_FILE = BASE_DIR / "database" / "zepto_books.db"


# -------------------------------------------------------------------
# Database schema
# -------------------------------------------------------------------

CREATE_CATEGORIES_TABLE = """
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE
);
"""

CREATE_BOOKS_TABLE = """
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price_gbp REAL NOT NULL,
    price_inr REAL NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    in_stock INTEGER NOT NULL CHECK (in_stock IN (0, 1)),
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
);
"""


# -------------------------------------------------------------------
# Database connection
# -------------------------------------------------------------------

def get_connection() -> sqlite3.Connection:
    """
    Create and configure the SQLite connection.
    """

    DATABASE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(DATABASE_FILE)

    # Enable foreign-key enforcement in SQLite.
    connection.execute("PRAGMA foreign_keys = ON;")

    return connection


# -------------------------------------------------------------------
# Create tables
# -------------------------------------------------------------------

def create_tables(connection: sqlite3.Connection) -> None:
    """
    Create the normalized categories and books tables.
    """

    cursor = connection.cursor()

    cursor.execute(CREATE_CATEGORIES_TABLE)
    cursor.execute(CREATE_BOOKS_TABLE)

    connection.commit()


# -------------------------------------------------------------------
# Insert categories
# -------------------------------------------------------------------

def insert_categories(
    connection: sqlite3.Connection,
    df: pd.DataFrame,
) -> None:
    """
    Insert each unique category into the categories table.
    """

    categories = sorted(
        df["category"].dropna().unique()
    )

    connection.executemany(
        """
        INSERT OR IGNORE INTO categories (category_name)
        VALUES (?);
        """,
        [(category,) for category in categories],
    )

    connection.commit()


# -------------------------------------------------------------------
# Insert books
# -------------------------------------------------------------------

def insert_books(
    connection: sqlite3.Connection,
    df: pd.DataFrame,
) -> None:
    """
    Insert cleaned books using category_id as a foreign key.
    """

    category_lookup = {
        row[1]: row[0]
        for row in connection.execute(
            """
            SELECT category_id, category_name
            FROM categories;
            """
        ).fetchall()
    }

    records = []

    for _, row in df.iterrows():

        category_id = category_lookup.get(
            row["category"]
        )

        if category_id is None:
            raise ValueError(
                f"Category not found in database: "
                f"{row['category']}"
            )

        records.append(
            (
                row["title"],
                float(row["price_gbp"]),
                float(row["price_inr"]),
                int(row["rating"]),
                int(bool(row["in_stock"])),
                category_id,
            )
        )

    connection.executemany(
        """
        INSERT INTO books (
            title,
            price_gbp,
            price_inr,
            rating,
            in_stock,
            category_id
        )
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        records,
    )

    connection.commit()


# -------------------------------------------------------------------
# Validation
# -------------------------------------------------------------------

def validate_database(
    connection: sqlite3.Connection,
    expected_book_count: int,
    expected_category_count: int,
) -> None:
    """
    Validate the database contents and relationship.
    """

    # Count categories.
    category_count = connection.execute(
        "SELECT COUNT(*) FROM categories;"
    ).fetchone()[0]

    # Count books.
    book_count = connection.execute(
        "SELECT COUNT(*) FROM books;"
    ).fetchone()[0]

    print(f"Categories in database: {category_count}")
    print(f"Books in database: {book_count}")

    if category_count != expected_category_count:
        raise ValueError(
            "Category count mismatch: "
            f"expected {expected_category_count}, "
            f"found {category_count}"
        )

    if book_count != expected_book_count:
        raise ValueError(
            "Book count mismatch: "
            f"expected {expected_book_count}, "
            f"found {book_count}"
        )

    # Check for books whose category_id doesn't exist.
    orphaned_books = connection.execute(
        """
        SELECT COUNT(*)
        FROM books AS b
        LEFT JOIN categories AS c
            ON b.category_id = c.category_id
        WHERE c.category_id IS NULL;
        """
    ).fetchone()[0]

    print(f"Orphaned books: {orphaned_books}")

    if orphaned_books != 0:
        raise ValueError(
            "Database contains books with invalid category_id values."
        )

    # Check foreign-key constraints.
    foreign_key_errors = connection.execute(
        "PRAGMA foreign_key_check;"
    ).fetchall()

    if foreign_key_errors:
        raise ValueError(
            f"Foreign-key validation failed: {foreign_key_errors}"
        )

    print("Foreign-key validation: passed")


# -------------------------------------------------------------------
# Display schema
# -------------------------------------------------------------------

def display_schema(connection: sqlite3.Connection) -> None:
    """
    Display the SQLite table definitions and columns.
    """

    print("\nDatabase tables:")

    tables = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
        """
    ).fetchall()

    for (table_name,) in tables:

        print(f"\nTable: {table_name}")

        columns = connection.execute(
            f"PRAGMA table_info({table_name});"
        ).fetchall()

        for column in columns:
            print(
                f"  column={column[1]}, "
                f"type={column[2]}, "
                f"not_null={column[3]}, "
                f"primary_key={column[5]}"
            )


# -------------------------------------------------------------------
# Main pipeline
# -------------------------------------------------------------------

def main() -> None:
    """
    Create and populate the normalized SQLite database.
    """

    print("Loading cleaned dataset...")

    df = pd.read_csv(CLEANED_FILE)

    print(f"Cleaned dataset shape: {df.shape}")

    # Remove an old database so every execution recreates
    # the database from the current cleaned CSV.
    if DATABASE_FILE.exists():
        DATABASE_FILE.unlink()

    connection = get_connection()

    try:
        print("\nCreating database tables...")
        create_tables(connection)

        print("Inserting categories...")
        insert_categories(connection, df)

        print("Inserting books...")
        insert_books(connection, df)

        print("\nValidating database...")
        validate_database(
            connection,
            expected_book_count=len(df),
            expected_category_count=df["category"].nunique(),
        )

        display_schema(connection)

    finally:
        connection.close()

    print(
        f"\nDatabase created successfully:\n"
        f"{DATABASE_FILE}"
    )


if __name__ == "__main__":
    main()