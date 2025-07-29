import pytest
from src.ev_cli_simulator.config_manager import ConfigManager, AgentConfig

def test_parse_charger_power_levels():
    """Tests if the power level string is parsed into a list of floats."""
    power_level_string = "[-11, -7.5, 0, 7.5, 11]"
    config_manager = ConfigManager()
    power_levels = config_manager.parse_charger_power_levels(power_level_string)
    assert power_levels == [-11.0, -7.5, 0.0, 7.5, 11.0]

def test_parse_agents():
    """Tests if agent strings are parsed into AgentConfig objects."""
    agent_strings = [
        "AgentV1:path/to/agent1.zip",
        "AgentV2:path/to/agent2.zip",
        "DumbAgent:baseline"
    ]
    config_manager = ConfigManager()
    parsed_agents = config_manager.parse_agents(agent_strings)

    assert len(parsed_agents) == 3
    assert isinstance(parsed_agents[0], AgentConfig)
    
    # Check the first agent
    assert parsed_agents[0].name == "AgentV1"
    assert parsed_agents[0].path == "path/to/agent1.zip"

    # Check the baseline agent
    assert parsed_agents[2].name == "DumbAgent"
    assert parsed_agents[2].path == "baseline"

def test_parse_agents_invalid_format():
    """Tests that an error is raised for a malformed agent string."""
    invalid_agent_string = ["AgentWithoutPath"]
    config_manager = ConfigManager()
    with pytest.raises(ValueError):
        config_manager.parse_agents(invalid_agent_string)
