import pytest
from src.ev_cli_simulator.core.battery import Battery

def test_battery_initialization():
    """Tests if the battery initializes with the correct properties."""
    battery = Battery(capacity_kwh=77.0, initial_soc=0.5)
    assert battery.capacity_kwh == 77.0
    assert battery.soc == 0.5

@pytest.mark.parametrize(
    "power_kw, duration_h, expected_soc",
    [
        (11, 1, 0.6428),    # Normal charging
        (-7, 2, 0.3182),   # Normal discharging
        (0, 5, 0.5),       # No power, no change
        (50, 2, 1.0),      # Attempted overcharge clamps to 1.0
        (-50, 2, 0.0),     # Attempted over-discharge clamps to 0.0
    ],
)
def test_update_soc(power_kw, duration_h, expected_soc):
    """Tests if the SOC updates correctly and clamps between 0.0 and 1.0."""
    battery = Battery(capacity_kwh=77.0, initial_soc=0.5)
    battery.update_soc(power_kw, duration_h)
    assert battery.soc == pytest.approx(expected_soc, abs=1e-4)

def test_battery_initialization_with_soh():
    """Tests if the battery initializes with correct SOH."""
    # Test default SOH
    battery1 = Battery(capacity_kwh=77.0)
    assert battery1.soh == 1.0

    # Test specific SOH
    battery2 = Battery(capacity_kwh=77.0, initial_soh=0.9)
    assert battery2.soh == 0.9

def test_degrade_soh():
    """Tests if the SOH degrades correctly and clamps at 0.0."""
    battery = Battery(capacity_kwh=77.0, initial_soh=1.0)

    battery.degrade(soh_loss=0.01)
    assert battery.soh == pytest.approx(0.99)

    battery.soh = 0.05 # Manually set for test case
    battery.degrade(soh_loss=0.1)
    assert battery.soh == 0.0
