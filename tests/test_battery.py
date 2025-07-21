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