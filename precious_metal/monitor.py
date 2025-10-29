from pathlib import Path
import sqlite3

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