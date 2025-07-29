# In your new tests/test_price_model.py file

import pytest
from datetime import datetime, timezone
from src.ev_cli_simulator.core.price_model import PriceModel

def test_get_price_for_timestamp():
    """Tests if the price model returns the correct price for a given hour."""
    csv_data = (
        "timestamp,price_eur_per_kwh\n"
        "2025-07-30T13:00:00Z,0.15\n"
        "2025-07-30T14:00:00Z,0.12\n"
    )
    price_model = PriceModel(csv_data)

    # Query for a time within the 13:00 hour
    query_time = datetime(2025, 7, 30, 13, 45, 0, tzinfo=timezone.utc)

    assert price_model.get_price(query_time) == 0.15