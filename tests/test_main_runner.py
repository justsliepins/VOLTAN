import pytest
from unittest.mock import MagicMock
from src.ev_cli_simulator.main import run_simulation_run
from src.ev_cli_simulator.config_manager import ScenarioConfig, AgentConfig

def test_run_simulation_run_with_multiple_agents(mocker):
    """
    Tests that the main loop correctly simulates multiple agents in parallel
    and respects the scenario window.
    """
    # --- Mocks and Spies ---
    mock_smart_agent = MagicMock()
    mock_smart_agent.predict.return_value = (0, None)

    # **FIX: Create a separate, configured mock for the DumbAgent**
    mock_dumb_agent = MagicMock()
    # The DumbAgent's predict method has a different signature
    mock_dumb_agent.predict.return_value = (1, None) # e.g., charge at max power

    mock_engine = MagicMock()
    mock_engine.run_step.return_value = {
        "costs": {"total_cost": 1.0}, "final_soc": 0.5, "final_soh": 0.99
    }
    
    mock_logger = MagicMock()
    
    # --- Configuration ---
    scenario = ScenarioConfig("Workday", 19, 23, 1.0) # 4-hour window
    
    # Define three agents to simulate
    agents_to_run = {
        "SmartAgent1": mock_smart_agent,
        "SmartAgent2": mock_smart_agent,
        "DumbAgent": mock_dumb_agent # Use the configured mock
    }

    config = {
        'run_id': 1,
        'years': 1/365, # 1 day
        'battery_capacity': 77.0,
        'max_charge_speed': 50.0,
        'charger_power_levels': [-11, 0, 11],
        'scenarios': [scenario],
        'price_path': 'dummy_path.csv',
        'soc_target': 0.8,
        'start_soc': 0.3
    }

    mocker.patch("builtins.open", mocker.mock_open(read_data="ts_start,price\n2025-01-01T00:00:00Z,0.1"))

    # --- Run the function ---
    run_simulation_run(config, agents_to_run, logger=mock_logger, engine_override=mock_engine)

    # --- Assertions ---
    steps_in_window = 16 # 4 hours * 4 steps/hour
    
    # Check call counts for smart agents
    assert mock_smart_agent.predict.call_count == steps_in_window * 2 # Called for SmartAgent1 and SmartAgent2
    # Check call count for the dumb agent
    assert mock_dumb_agent.predict.call_count == steps_in_window

    # Engine is called for each agent for each step in the window
    assert mock_engine.run_step.call_count == steps_in_window * 3
    assert mock_logger.log_step.call_count == steps_in_window * 3