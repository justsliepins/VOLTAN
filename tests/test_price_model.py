import csv
import io
from datetime import datetime, timezone, timedelta

class PriceModel:
    """
    Models electricity prices by loading hourly data from a CSV source.
    Handles Daylight Saving Time transitions and loops data for long-term simulations.
    """
    def __init__(self, price_data_csv: str):
        """
        Initializes the PriceModel by parsing CSV data into a lookup dictionary.

        Args:
            price_data_csv (str): A string containing the price data in CSV format.
                                  Expected headers: 'ts_start', 'price'.
        """
        self._prices = {}
        self._base_year_map = {}
        min_year = 9999
        max_year = 0

        csv_file = io.StringIO(price_data_csv)
        reader = csv.DictReader(csv_file)

        for row in reader:
            timestamp_str = row['ts_start']
            price = float(row['price'])
            
            # This parsing is robust to different timezone formats
            if 'Z' in timestamp_str:
                 timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            elif '+' in timestamp_str:
                 timestamp = datetime.fromisoformat(timestamp_str)
            else:
                 ts_naive = datetime.fromisoformat(timestamp_str)
                 timestamp = ts_naive.replace(tzinfo=timezone.utc)

            self._prices[timestamp] = price
            
            # Keep track of the range of years in the data
            min_year = min(min_year, timestamp.year)
            max_year = max(max_year, timestamp.year)

        # Create a map for looping data. For each day of a leap year,
        # it stores the corresponding date in a year that exists in the data.
        if min_year <= max_year:
            for day_of_year in range(1, 367):
                try:
                    base_date = datetime(2024, 1, 1) + timedelta(days=day_of_year - 1) # 2024 is a leap year
                    target_year = min_year + ((base_date.year - min_year) % (max_year - min_year + 1))
                    looped_date = base_date.replace(year=target_year)
                    self._base_year_map[(base_date.month, base_date.day)] = (looped_date.month, looped_date.day, looped_date.year)
                except ValueError:
                    continue # Skip Feb 29 if target year is not a leap year


    def get_price(self, timestamp: datetime) -> float | None:
        """
        Gets the electricity price for the hour corresponding to the given timestamp.
        Handles data looping for long simulations and DST gaps.
        """
        lookup_time = timestamp.replace(minute=0, second=0, microsecond=0)

        # --- Data Looping Logic ---
        # Find the corresponding date in a year for which we have data
        month, day, year = self._base_year_map.get((lookup_time.month, lookup_time.day), (lookup_time.month, lookup_time.day, lookup_time.year))
        try:
            looped_lookup_time = lookup_time.replace(year=year, month=month, day=day)
        except ValueError: # Handle Feb 29 in non-leap years
            looped_lookup_time = lookup_time.replace(year=year, month=month, day=28)

        price = self._prices.get(looped_lookup_time)

        # --- DST Handling ---
        # If price is not found (e.g., during DST spring forward),
        # use the price from the previous hour.
        if price is None:
            previous_hour = looped_lookup_time - timedelta(hours=1)
            return self._prices.get(previous_hour)

        return price
