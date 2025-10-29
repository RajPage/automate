from datetime import datetime
from pathlib import Path
import sqlite3
import statistics
import requests

class PriceHistory:
    def __init__(self, db_path='price_history.db'):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        """Initialize the database and create the table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        with open('schema.sql', 'r') as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
        
        conn.commit()
        conn.close()

    def add_price(self, date, metal, price):
        """Add a new price entry to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        with open('insert_price.sql', 'r') as f:
            sql_insert = f.read()
        cursor.execute(sql_insert, (date, metal, price))

        conn.commit()
        conn.close()


    def get_prices(self, metal, days=None):
        """Retrieve all price entries for a specific metal."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if days is not None:
            with open('select_recent.sql', 'r') as f:
                sql_select_recent = f.read()
            cursor.execute(sql_select_recent, (metal, days))
        else:
            with open('select_all.sql', 'r') as f:
                sql_select = f.read()
            cursor.execute(sql_select, (metal,))
        prices = [row[0] for row in cursor.fetchall()] # Flatten list of tuples

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
            'average': avg_price,
            'min': min_price,
            'max': max_price,
            'count': len(prices)
        }
    
    # TODO: Clean up old data method


class PriceFetcher:
    """Class to fetch current prices from an external API"""
    Gold_Silver_API_URL = 'https://data-asg.goldprice.org/dbXRates/INR'
    Gold_key = 'xauPrice'
    Silver_key = 'xagPrice'
    # X means precious metals, AU means gold, AG means silver
    @staticmethod
    def fetch_current_price_in_inr():
        try:
            # TODO: Replace with another API with better reliability if needed
            response = requests.get(PriceFetcher.Gold_Silver_API_URL, timeout=10)
            if response.status_code != 200:
                print(f"Error fetching price data: Status code {response.status_code}")
                return None
            
            data = response.json()
            gold_per_oz = float(data['items'][0][PriceFetcher.Gold_key])
            silver_per_oz = float(data['items'][0][PriceFetcher.Silver_key])

            gold_per_10g = PriceFetcher.convert_oz_to_grams(gold_per_oz, grams=10)
            silver_per_10g = PriceFetcher.convert_oz_to_grams(silver_per_oz, grams=10)

            return {
                'gold': round(gold_per_10g, 2),
                'silver': round(silver_per_10g, 2),
                'timestamp': datetime.now().isoformat()
            }

        except requests.RequestException as e:
            print(f"Error fetching price data: {e}")
            return None
        
    @staticmethod
    def convert_oz_to_grams(price_per_oz, grams=10):
        grams_per_oz = 31.1035
        return (price_per_oz / grams_per_oz) * grams
    
if __name__ == "__main__":
    fetcher = PriceFetcher()
    prices = fetcher.fetch_current_price_in_inr()
    if prices:
        print(f"Current Gold Price (10g): INR {prices['gold']}")
        print(f"Current Silver Price (10g): INR {prices['silver']}")