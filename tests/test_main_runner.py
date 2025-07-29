import pytest
from unittest.mock import MagicMock
from src.ev_cli_simulator.main import run_simulation_run
from src.ev_cli_simulator.config_manager import ScenarioConfig, ChargerConfig

def test_run_simulation_run_respects_scenario_window(mocker):
    """
    Tests that the main loop only calls the agent and engine during the
    hours specified by the daily charging scenario and logs a daily summary.
    """
    # --- Mocks and Spies ---
    # We replace the real objects with mocks that we can spy on.
    mock_agent = MagicMock()
    mock_agent.predict.return_value = (0, None) # Always return 'idle' action

    mock_engine = MagicMock()
    # Define a return value that includes the 'costs' dictionary
    mock_engine.run_step.return_value = {
        "costs": {
            "electricity_cost": 1.0,
            "calendar_cost": 0.1,
            "cyclic_cost": 0.2,
            "total_cost": 1.3
        },
        "final_soc": 0.5,
        "final_soh": 0.99
    }

    mock_logger = MagicMock()
    
    # --- Configuration ---
    # A 1-day run with a 4-hour charging window (16 steps of 15 mins)
    workday_scenario = ScenarioConfig("Workday", 19, 23, 1.0) # 7 PM to 11 PM
    # Provide a dummy charger with at least two power levels for the DumbAgent logic
    dummy_charger = ChargerConfig("Dummy", [0, 6], 0, 24)

    config = {
        'run_id': 1,
        'years': 1/365, # Run for 1 day
        'battery_capacity': 77.0,
        'max_charge_speed': 50.0,
        'chargers': [dummy_charger],
        'scenarios': [workday_scenario],
        'price_path': 'dummy_path.csv', # Required by the function signature
        'soc_target': 0.8 # **NEW: Add the required soc_target**
    }

    # Mock the 'open' function to prevent a FileNotFoundError when the PriceModel is created
    mocker.patch("builtins.open", mocker.mock_open(read_data="ts_start,price\n2025-01-01T00:00:00Z,0.1"))

    # --- Run the function we are testing ---
    run_simulation_run(config, smart_agent=mock_agent, logger=mock_logger, engine_override=mock_engine)

    # --- Assertions ---
    # A 4-hour window has 16 steps (4 * 4)
    total_steps_in_window = 16
    
    # The smart agent's predict method should be called once per step in the window
    assert mock_agent.predict.call_count == total_steps_in_window
    
    # The engine's run_step method is called for both the smart and dumb agent
    assert mock_engine.run_step.call_count == total_steps_in_window * 2
    
    # **FIX: The logger is now only called ONCE per agent at the END of the day**
    assert mock_logger.log_step.call_count == 2
