import pytest
from unittest.mock import MagicMock
from src.ev_cli_simulator.main import run_simulation_run
from src.ev_cli_simulator.config_manager import ScenarioConfig, ChargerConfig

def test_run_simulation_run_respects_scenario_window(mocker):
    """
    Tests that the main loop only calls the agent and engine during the
    hours specified by the daily charging scenario and logs every step.
    """
    # --- Mocks and Spies ---
    mock_agent = MagicMock()
    mock_agent.predict.return_value = (0, None) # Always idle

    mock_engine = MagicMock()
    mock_engine.run_step.return_value = {
        "costs": {"total_cost": 1.0}, "final_soc": 0.5, "final_soh": 0.99
    }
    
    mock_logger = MagicMock()
    
    # --- Configuration ---
    workday_scenario = ScenarioConfig("Workday", 19, 23, 1.0) # 4-hour window
    dummy_charger = ChargerConfig("Dummy", [0, 6], 0, 24)

    config = {
        'run_id': 1,
        'years': 1/365, # Run for 1 day
        'battery_capacity': 77.0,
        'max_charge_speed': 50.0,
        'chargers': [dummy_charger],
        'scenarios': [workday_scenario],
        'price_path': 'dummy_path.csv',
        'soc_target': 0.8
    }

    mocker.patch("builtins.open", mocker.mock_open(read_data="ts_start,price\n2025-01-01T00:00:00Z,0.1"))

    # --- Run the function ---
    run_simulation_run(config, smart_agent=mock_agent, logger=mock_logger, engine_override=mock_engine)

    # --- Assertions ---
    total_steps_in_window = 16 # 4 hours * 4 steps/hour
    
    assert mock_agent.predict.call_count == total_steps_in_window
    assert mock_engine.run_step.call_count == total_steps_in_window * 2
    
    # The logger is called for every step inside the window for both agents.
    assert mock_logger.log_step.call_count == total_steps_in_window * 2
