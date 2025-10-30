"""Module to monitor and store precious metal prices over time."""

from datetime import datetime
from pathlib import Path
import sqlite3
import requests


class PriceHistory:
    """Class to manage the price history database for precious metals."""

    def __init__(self, db_path="price_history.db"):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        """Initialize the database and create the table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        with open("schema.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
        cursor.executescript(sql_script)

        conn.commit()
        conn.close()

    def add_price(self, date, metal, price):
        """Add a new price entry to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        with open("insert_price.sql", "r", encoding="utf-8") as f:
            sql_insert = f.read()
        cursor.execute(sql_insert, (date, metal, price))

        conn.commit()
        conn.close()

    def get_prices(self, metal, days=None):
        """Retrieve all price entries for a specific metal."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if days is not None:
            with open("select_recent.sql", "r", encoding="utf-8") as f:
                sql_select_recent = f.read()
            cursor.execute(sql_select_recent, (metal, days))
        else:
            with open("select_all.sql", "r", encoding="utf-8") as f:
                sql_select = f.read()
            cursor.execute(sql_select, (metal,))
        prices = [row[0] for row in cursor.fetchall()]  # Flatten list of tuples

        if days:
            prices = prices[::-1]  # Reverse to chronological order

        conn.close()
        return prices

    def get_analytics(self, metal, days=30):
        """Compute analytics like average, min, max prices for a specific metal."""
        prices = self.get_prices(metal, days)
        if not prices:
            return None

        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)

        return {
            "average": avg_price,
            "min": min_price,
            "max": max_price,
            "count": len(prices),
        }

    # TODO: Clean up old data method # pylint: disable=fixme


class PriceFetcher:
    """Class to fetch current prices from an external API"""

    Gold_Silver_API_URL = "https://data-asg.goldprice.org/dbXRates/INR"
    Gold_key = "xauPrice"
    Silver_key = "xagPrice"

    # X means precious metals, AU means gold, AG means silver
    @staticmethod
    def fetch_current_price_in_inr():
        """Fetch current gold and silver prices in INR per 10 grams."""
        try:
            # TODO: Replace with another API with better reliability if needed # pylint: disable=fixme
            response = requests.get(
                PriceFetcher.Gold_Silver_API_URL,
                timeout=10,
                headers=PriceFetcher.get_headers(),
            )
            if response.status_code != 200:
                print(f"Error fetching price data: Status code {response.status_code}")
                return None

            data = response.json()
            gold_per_oz = float(data["items"][0][PriceFetcher.Gold_key])
            silver_per_oz = float(data["items"][0][PriceFetcher.Silver_key])

            gold_per_10g = PriceFetcher.convert_oz_to_grams(gold_per_oz, grams=10)
            silver_per_10g = PriceFetcher.convert_oz_to_grams(silver_per_oz, grams=10)

            return {
                "gold": round(gold_per_10g, 2),
                "silver": round(silver_per_10g, 2),
                "timestamp": datetime.now().isoformat(),
            }

        except requests.RequestException as e:
            print(f"Error fetching price data: {e}")
            return None

    @staticmethod
    def convert_oz_to_grams(price_per_oz, grams=10):
        """Convert price from per troy ounce to per specified grams."""
        grams_per_oz = 31.1035
        return (price_per_oz / grams_per_oz) * grams

    @staticmethod
    def get_headers():
        """Mimic a browser request to avoid potential 403 Forbidden by the server."""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://goldprice.org/",
        }


if __name__ == "__main__":
    fetcher = PriceFetcher()
    current_prices = fetcher.fetch_current_price_in_inr()
    if current_prices:
        print(f"Current Gold Price (10g): INR {current_prices['gold']}")
        print(f"Current Silver Price (10g): INR {current_prices['silver']}")
