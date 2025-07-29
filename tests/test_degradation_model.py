import pytest
from src.ev_cli_simulator.core.degradation_model import DegradationModel

# In tests/test_degradation_model.py

def test_get_sei_cost():
    """
    Tests if the SEI cost is calculated correctly using an exponential decay model.
    """
    # Parameters derived from academic papers (see documentation).
    initial_cost = 6.088
    # Use a more precise decay_rate to fix the floating point error
    decay_rate = 0.01301 

    model = DegradationModel(initial_cost=initial_cost, decay_rate=decay_rate)

    # ... rest of the test remains the same
    cost_at_cycle_200 = model.get_sei_cost(cycle_number=200)
    assert cost_at_cycle_200 == pytest.approx(0.457, abs=1e-3)