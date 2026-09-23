from pathlib import Path

import pandas as pd


# -------------------------------------------------------------------
# File paths
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
RAW_FILE = BASE_DIR / "data" / "raw_books.csv"
CLEANED_FILE = BASE_DIR / "data" / "cleaned_books.csv"

# Fixed project exchange rate.
# This is intentionally NOT fetched from the internet.
GBP_TO_INR = 105.50


# -------------------------------------------------------------------
# Rating mapping
# -------------------------------------------------------------------

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

def parse_price(value):
    """
    Convert a scraped GBP price into a numeric float.

    Handles both the normal pound symbol (£) and the common
    UTF-8/Latin-1 encoding artifact (Â£).
    """
    if pd.isna(value):
        return None

    text = str(value).strip()

    # Handle encoding artifact and normal currency symbol.
    text = text.replace("Â£", "").replace("£", "").strip()

    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def parse_rating(value):
    """
    Convert textual star rating into an integer from 1 to 5.
    """
    if pd.isna(value):
        return None

    text = str(value).strip().title()

    return RATING_MAP.get(text)


def parse_availability(value):
    """
    Convert availability text into a boolean.

    'In stock' -> True
    Other recognized/non-stock text -> False
    Unparseable values -> None
    """
    if pd.isna(value):
        return None

    text = str(value).strip().lower()

    if "in stock" in text:
        return True

    if "out of stock" in text:
        return False

    return None


# -------------------------------------------------------------------
# Cleaning
# -------------------------------------------------------------------

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and enrich the raw scraped dataset.
    """

    required_columns = {
        "title",
        "price_gbp",
        "rating",
        "availability",
        "category",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    cleaned = df.copy()

    # ---------------------------------------------------------------
    # Basic text cleaning
    # ---------------------------------------------------------------

    for column in ["title", "availability", "category"]:
        cleaned[column] = cleaned[column].astype("string").str.strip()

    # ---------------------------------------------------------------
    # Convert price GBP
    # ---------------------------------------------------------------

    cleaned["price_gbp"] = cleaned["price_gbp"].apply(parse_price)

    # ---------------------------------------------------------------
    # Convert textual rating
    # ---------------------------------------------------------------

    cleaned["rating"] = cleaned["rating"].apply(parse_rating)

    # ---------------------------------------------------------------
    # Convert availability to boolean
    # ---------------------------------------------------------------

    cleaned["in_stock"] = cleaned["availability"].apply(
        parse_availability
    )

    # The original textual availability column is no longer needed
    # after conversion.
    cleaned = cleaned.drop(columns=["availability"])

    # ---------------------------------------------------------------
    # Handle numeric parsing failures
    # ---------------------------------------------------------------

    numeric_columns = ["price_gbp", "rating"]

    for column in numeric_columns:
        invalid_count = cleaned[column].isna().sum()

        if invalid_count > 0:
            median_value = cleaned[column].median()

            if pd.isna(median_value):
                raise ValueError(
                    f"Cannot median-impute column '{column}' because "
                    "no valid numeric values are available."
                )

            print(
                f"{column}: {invalid_count} parsing failure(s). "
                f"Median-imputing with {median_value}."
            )

            cleaned[column] = cleaned[column].fillna(median_value)

    # ---------------------------------------------------------------
    # Handle availability parsing failures
    # ---------------------------------------------------------------

    invalid_stock_count = cleaned["in_stock"].isna().sum()

    if invalid_stock_count > 0:
        print(
            f"in_stock: {invalid_stock_count} parsing failure(s). "
            "Dropping affected rows."
        )

        cleaned = cleaned.dropna(subset=["in_stock"])

    # ---------------------------------------------------------------
    # Handle essential text fields
    # ---------------------------------------------------------------

    before_drop = len(cleaned)

    cleaned = cleaned.dropna(
        subset=["title", "category"]
    )

    dropped_text_rows = before_drop - len(cleaned)

    if dropped_text_rows > 0:
        print(
            f"Dropped {dropped_text_rows} rows with missing "
            "title/category."
        )

    # ---------------------------------------------------------------
    # Fixed GBP → INR conversion
    # ---------------------------------------------------------------

    cleaned["price_inr"] = (
        cleaned["price_gbp"] * GBP_TO_INR
    )

    # ---------------------------------------------------------------
    # Enforce final data types
    # ---------------------------------------------------------------

    cleaned["price_gbp"] = cleaned["price_gbp"].astype(float)
    cleaned["price_inr"] = cleaned["price_inr"].astype(float)
    cleaned["rating"] = cleaned["rating"].astype(int)
    cleaned["in_stock"] = cleaned["in_stock"].astype(bool)

    # Remove duplicate book/category combinations.
    cleaned = cleaned.drop_duplicates(
        subset=["title", "category"],
        keep="first",
    ).reset_index(drop=True)

    # Final column order.
    cleaned = cleaned[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category",
        ]
    ]

    return cleaned


# -------------------------------------------------------------------
# Validation
# -------------------------------------------------------------------

def validate_cleaned_data(df: pd.DataFrame) -> None:
    """
    Validate the final cleaned dataset against Module 1 requirements.
    """

    expected_columns = [
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "in_stock",
        "category",
    ]

    if list(df.columns) != expected_columns:
        raise ValueError(
            "Final columns do not match the required schema.\n"
            f"Expected: {expected_columns}\n"
            f"Found: {list(df.columns)}"
        )

    if len(df) < 60:
        raise ValueError(
            f"Only {len(df)} cleaned rows remain. "
            "At least 60 are required."
        )

    if df["category"].nunique() < 3:
        raise ValueError(
            "The cleaned dataset must contain at least "
            "3 categories."
        )

    if not df["price_gbp"].dtype == "float64":
        raise ValueError("price_gbp must be float.")

    if not df["price_inr"].dtype == "float64":
        raise ValueError("price_inr must be float.")

    if not pd.api.types.is_integer_dtype(df["rating"]):
        raise ValueError("rating must be an integer.")

    if not pd.api.types.is_bool_dtype(df["in_stock"]):
        raise ValueError("in_stock must be boolean.")

    if not df["rating"].between(1, 5).all():
        raise ValueError("rating values must be between 1 and 5.")

    # Verify the fixed exchange-rate calculation.
    expected_inr = df["price_gbp"] * GBP_TO_INR

    if not expected_inr.round(10).equals(
        df["price_inr"].round(10)
    ):
        raise ValueError(
            "price_inr contains incorrect GBP → INR conversions."
        )

    if df.isna().any().any():
        raise ValueError(
            "The final cleaned dataset contains missing values."
        )


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main() -> None:
    """Run the complete cleaning process."""

    print("Loading raw scraped data...")

    df = pd.read_csv(RAW_FILE)

    print(f"Raw shape: {df.shape}")

    print("\nRaw data types:")
    print(df.dtypes)

    print("\nRaw missing values:")
    print(df.isna().sum())

    cleaned_df = clean_data(df)

    validate_cleaned_data(cleaned_df)

    CLEANED_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cleaned_df.to_csv(
        CLEANED_FILE,
        index=False,
    )

    print("\nCleaning completed successfully.")
    print(f"Cleaned shape: {cleaned_df.shape}")
    print(f"Saved to: {CLEANED_FILE}")

    print("\nCleaned data types:")
    print(cleaned_df.dtypes)

    print("\nCleaned dataset:")
    print(cleaned_df.head().to_string(index=False))

    print("\nBooks per category:")
    print(cleaned_df["category"].value_counts())

    print("\nRating distribution:")
    print(cleaned_df["rating"].value_counts().sort_index())

    print("\nStock distribution:")
    print(cleaned_df["in_stock"].value_counts())

    print("\nTotal GBP:")
    print(f"{cleaned_df['price_gbp'].sum():.2f}")

    print("\nTotal INR:")
    print(f"{cleaned_df['price_inr'].sum():.2f}")


if __name__ == "__main__":
    main()