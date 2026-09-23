import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com"
OUTPUT_FILE = Path(__file__).parent / "data" / "raw_books.csv"

# We use category pages so the final dataset is guaranteed to
# contain books from at least three different categories.
CATEGORY_COUNT_REQUIRED = 3
MIN_BOOKS_REQUIRED = 60

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ZeptoDataPipeline/1.0)"
}


def fetch_page(url: str) -> BeautifulSoup:
    """Fetch a webpage and return its parsed BeautifulSoup object."""
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def discover_categories() -> dict[str, str]:
    """Discover category names and URLs from the Books to Scrape website."""
    soup = fetch_page(f"{BASE_URL}/")

    categories = {}

    for link in soup.select("div.side_categories ul li ul li a"):
        category_name = link.get_text(strip=True)
        href = link.get("href")

        if category_name and href:
            categories[category_name] = href

    if len(categories) < CATEGORY_COUNT_REQUIRED:
        raise ValueError(
            f"Only {len(categories)} categories were discovered. "
            f"At least {CATEGORY_COUNT_REQUIRED} are required."
        )

    return categories

def parse_rating(rating_element) -> str:
    """Extract the star-rating text such as 'Three'."""
    if rating_element is None:
        return ""

    classes = rating_element.get("class", [])

    for rating in ["One", "Two", "Three", "Four", "Five"]:
        if rating in classes:
            return rating

    return ""


def parse_book_card(card, category: str) -> dict:
    """Extract the required fields from one book listing card."""
    title_element = card.select_one("h3 a")
    price_element = card.select_one(".price_color")
    rating_element = card.select_one(".star-rating")
    availability_element = card.select_one(".availability")

    return {
        "title": title_element.get("title", "").strip()
        if title_element
        else "",
        "price_gbp": price_element.get_text(strip=True)
        if price_element
        else "",
        "rating": parse_rating(rating_element),
        "availability": availability_element.get_text(" ", strip=True)
        if availability_element
        else "",
        "category": category,
    }


def scrape_category(category: str, relative_url: str) -> list[dict]:
    """Scrape all paginated books from one category."""
    books = []
    page_url = f"{BASE_URL}/{relative_url}"

    while page_url:
        print(f"Scraping {category}: {page_url}")

        soup = fetch_page(page_url)

        book_cards = soup.select("article.product_pod")

        for card in book_cards:
            books.append(parse_book_card(card, category))

        next_link = soup.select_one("li.next a")

        if next_link:
            next_href = next_link.get("href")
            current_page_url = page_url.rsplit("/", 1)[0]
            page_url = f"{current_page_url}/{next_href}"
        else:
            page_url = None

        time.sleep(0.2)

    return books


def scrape_all_categories() -> pd.DataFrame:
    """Discover categories and scrape until all requirements are satisfied."""

    categories = discover_categories()

    # Use deterministic alphabetical ordering.
    selected_categories = sorted(categories.items())

    print("\nAvailable categories discovered:")
    print(f"Total categories discovered: {len(categories)}")

    all_books = []

    for category, relative_url in selected_categories:
        category_books = scrape_category(category, relative_url)

        print(
            f"{category}: {len(category_books)} books collected"
        )

        all_books.extend(category_books)

        # Check both project requirements after each category.
        current_category_count = len(
            set(book["category"] for book in all_books)
        )

        if (
            len(all_books) >= MIN_BOOKS_REQUIRED
            and current_category_count >= CATEGORY_COUNT_REQUIRED
        ):
            print(
                "\nMinimum scraping requirements reached:"
            )
            print(
                f"- Books: {len(all_books)}"
            )
            print(
                f"- Categories: {current_category_count}"
            )
            break

    df = pd.DataFrame(all_books)

    df = df.drop_duplicates(
        subset=["title", "category"],
        keep="first"
    ).reset_index(drop=True)

    return df


def validate_scraped_data(df: pd.DataFrame) -> None:
    """Validate the minimum Module 1 scraping requirements."""
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

    category_count = df["category"].nunique()
    row_count = len(df)

    print(f"\nTotal scraped rows: {row_count}")
    print(f"Unique categories: {category_count}")
    
    if row_count < MIN_BOOKS_REQUIRED:
        raise ValueError(
            f"Only {row_count} books were scraped. "
            f"At least {MIN_BOOKS_REQUIRED} are required."
        )
    if category_count < CATEGORY_COUNT_REQUIRED:
        raise ValueError(
            f"Only {category_count} categories were scraped. "
            f"At least {CATEGORY_COUNT_REQUIRED} are required."
       
        )
    


def main() -> None:
    """Run the complete scraping process."""
    print("Starting book scraping...\n")

    df = scrape_all_categories()

    validate_scraped_data(df)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("\nScraping completed successfully.")
    print(f"Saved dataset to: {OUTPUT_FILE}")
    print("\nFirst 5 rows:")
    print(df.head())

    print("\nBooks per category:")
    print(df["category"].value_counts())


if __name__ == "__main__":
    main()