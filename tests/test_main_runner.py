# In a new file: tests/test_main_runner.py

import pytest
from unittest.mock import MagicMock
from src.ev_cli_simulator.main import run_simulation_run
from src.ev_cli_simulator.config_manager import ChargerConfig

def test_run_simulation_run(mocker):
    """
    Integration test for a single simulation run.
    Uses mocks to verify that the main loop calls components correctly.
    """
    # --- Mocks and Spies ---
    # We replace the real objects with mocks that we can spy on.
    mock_agent = MagicMock()
    mock_agent.predict.return_value = (3, None) # Always return 'idle' action

    mock_engine = MagicMock()
    mock_engine.run_step.return_value = {
        "costs": {"total_cost": 1.0}, "final_soc": 0.5, "final_soh": 0.99
    }

    mock_logger = MagicMock()
    
    # --- Configuration ---
    # A minimal config for a very short run (2 days)
    config = {
        'run_id': 1,
        'years': 1/365 * 2, # Run for 2 days
        'battery_capacity': 77.0,
        'max_charge_speed': 50.0,
        'chargers': [ChargerConfig("Home", [0], 0, 24)] # Charge anytime
    }

    # --- Run the function we are testing ---
    run_simulation_run(config, smart_agent=mock_agent, logger=mock_logger, engine_override=mock_engine)

    # --- Assertions ---
    # A 2-day simulation with 15-min steps = 2 * 96 = 192 steps
    # We check if our mocked methods were called the correct number of times.
    assert mock_agent.predict.call_count == 192
    assert mock_engine.run_step.call_count == 192 * 2 # Called for both smart and dumb agent
    assert mock_logger.log_step.call_count == 192 * 2