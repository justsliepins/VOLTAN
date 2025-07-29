import pytest
from datetime import datetime, timezone
from src.ev_cli_simulator.core.cost_calculator import CostCalculator
from src.ev_cli_simulator.core.price_model import PriceModel

# --- Mock Objects for Testing ---

class MockDegradationModel:
    """A fake DegradationModel that returns fixed values for testing."""
    def get_calendar_ageing_cost(self, soc, duration_h):
        return 0.1  # Always return a fixed cost

    def get_cyclic_ageing_cost(self, c_rate, cycle_portion):
        return 0.3  # Always return a fixed cost

@pytest.fixture
def calculator_setup():
    """Sets up the PriceModel, mock DegradationModel, and CostCalculator."""
    # **FIX: Use the correct column headers 'ts_start' and 'price'**
    csv_data = "ts_start,price\n2025-01-01T10:00:00Z,0.15"
    price_model = PriceModel(csv_data)
    degradation_model = MockDegradationModel()
    cost_calculator = CostCalculator(
        price_model=price_model,
        degradation_model=degradation_model
    )
    return cost_calculator

# --- The Actual Test ---

def test_calculate_step_costs(calculator_setup):
    """
    Tests if the CostCalculator correctly orchestrates the models and
    sums the individual costs to produce a correct total cost.
    """
    cost_calculator = calculator_setup

    # Define the parameters for the charging step
    power_kw = 11.0
    duration_h = 1.0
    timestamp = datetime(2025, 1, 1, 10, 30, tzinfo=timezone.utc)
    battery_capacity_kwh = 77.0
    soc = 0.5
    cycle_number = 1 # Not used by mock, but required by the method signature

    # Calculate the costs
    costs = cost_calculator.calculate_step_costs(
        power_kw=power_kw,
        duration_h=duration_h,
        timestamp=timestamp,
        battery_capacity_kwh=battery_capacity_kwh,
        soc=soc,
        cycle_number=cycle_number
    )

    # --- Assertions ---
    # Expected electricity cost: 11 kW * 1 h * 0.15 €/kWh = 1.65
    assert costs['electricity_cost'] == pytest.approx(1.65)

    # Expected degradation costs from our mock model
    assert costs['calendar_cost'] == pytest.approx(0.1)
    assert costs['cyclic_cost'] == pytest.approx(0.3)
    
    # Expected total cost: 1.65 + 0.1 + 0.3 = 2.05
    assert costs['total_cost'] == pytest.approx(2.05)