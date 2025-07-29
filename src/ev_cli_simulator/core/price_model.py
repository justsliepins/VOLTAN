import csv
import io
from datetime import datetime, timezone

class PriceModel:
    """
    Models electricity prices by loading hourly data from a CSV source.
    """
    def __init__(self, price_data_csv: str):
        """
        Initializes the PriceModel by parsing CSV data into a lookup dictionary.

        Args:
            price_data_csv (str): A string containing the price data in CSV format.
                                  Expected headers: 'timestamp', 'price_eur_per_kwh'.
        """
        self._prices = {}
        # Use io.StringIO to treat the string as a file for the csv reader
        csv_file = io.StringIO(price_data_csv)
        reader = csv.DictReader(csv_file)

        for row in reader:
            # Parse the timestamp string into a timezone-aware datetime object
            timestamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
            price = float(row['price_eur_per_kwh'])
            self._prices[timestamp] = price

    def get_price(self, timestamp: datetime) -> float | None:
        """
        Gets the electricity price for the hour corresponding to the given timestamp.

        Args:
            timestamp (datetime): The specific time to query for a price.

        Returns:
            float | None: The price for that hour, or None if not found.
        """
        # Truncate the query timestamp to the beginning of the hour
        # This makes it a valid key for our hourly price dictionary
        lookup_time = timestamp.replace(minute=0, second=0, microsecond=0)

        return self._prices.get(lookup_time)