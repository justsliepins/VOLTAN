import pytest
from datetime import datetime, timezone
from src.ev_cli_simulator.core.simulation_engine import SimulationEngine
from src.ev_cli_simulator.core.battery import Battery

# --- Mock Object for Testing ---

class MockCostCalculator:
    """A fake CostCalculator that returns a fixed dictionary of costs."""
    def calculate_step_costs(self, **kwargs):
        # The values here are chosen to match the test case's expectations.
        return {
            "electricity_cost": 1.65,
            "calendar_cost": 0.1,
            "cyclic_cost": 0.3,
            "total_cost": 2.05, # This is now irrelevant for SOH calculation
        }

# --- The Actual Test ---

def test_run_step():
    """
    Tests if the SimulationEngine correctly orchestrates the models to update
    the battery's state (SOC and SOH) and return the correct results.
    """
    # 1. Setup
    battery = Battery(capacity_kwh=77.0, initial_soc=0.5, initial_soh=1.0)
    mock_calculator = MockCostCalculator()
    battery_eol_cost = 8000.0  # €8000 cost for a 20% SOH loss

    engine = SimulationEngine(
        battery=battery,
        cost_calculator=mock_calculator,
        battery_eol_cost=battery_eol_cost
    )

    # 2. Action
    step_results = engine.run_step(
        power_kw=11.0,
        duration_h=1.0,
        timestamp=datetime.now(timezone.utc), # Timestamp doesn't matter for this test
        cycle_number=1
    )

    # 3. Assertions
    # Assert battery state was updated correctly
    assert battery.soc == pytest.approx(0.6428, abs=1e-4)

    # **FIX: Update the expected SOH calculation to match the new logic.**
    # The physical degradation is now only calendar + cyclic cost.
    # physical_cost = 0.1 + 0.3 = 0.4
    # soh_loss = (0.4 / 8000) * 0.20 = 0.00001
    # new_soh = 1.0 - 0.00001 = 0.99999
    assert battery.soh == pytest.approx(0.99999)

    # Assert the returned dictionary has the correct information
    assert step_results['final_soc'] == battery.soc
    assert step_results['final_soh'] == battery.soh
    assert step_results['costs']['total_cost'] == 2.05