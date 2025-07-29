import pytest
from src.ev_cli_simulator.config_manager import ConfigManager, ChargerConfig, ScenarioConfig

def test_parse_chargers():
    """Tests if the charger definition strings are parsed correctly into ChargerConfig objects."""
    charger_strings = [
        "Home:[-6,0,6]:19-07",
        "Work:[-11,0,11]:09-17"
    ]
    
    config_manager = ConfigManager()
    parsed_chargers = config_manager.parse_chargers(charger_strings)

    assert len(parsed_chargers) == 2
    assert isinstance(parsed_chargers[0], ChargerConfig)

    # Check the first charger's attributes
    assert parsed_chargers[0].name == "Home"
    assert parsed_chargers[0].power_levels == [-6, 0, 6]
    assert parsed_chargers[0].start_hour == 19
    assert parsed_chargers[0].end_hour == 7

    # Check the second charger's attributes
    assert parsed_chargers[1].name == "Work"
    assert parsed_chargers[1].power_levels == [-11, 0, 11]
    assert parsed_chargers[1].start_hour == 9
    assert parsed_chargers[1].end_hour == 17

def test_parse_chargers_invalid_format():
    """Tests if the parser raises an error for malformed strings."""
    # This string is missing the time window
    invalid_charger_string = ["Home:[-6,0,6]"]
    
    config_manager = ConfigManager()
    
    # Use pytest.raises to assert that a ValueError is thrown
    with pytest.raises(ValueError):
        config_manager.parse_chargers(invalid_charger_string)

def test_parse_scenarios_success():
    """Tests if valid scenario strings are parsed correctly."""
    scenario_strings = [
        "Workday:19-07:0.8",
        "Holiday:00-24:0.2"
    ]
    
    config_manager = ConfigManager()
    parsed_scenarios = config_manager.parse_scenarios(scenario_strings)

    assert len(parsed_scenarios) == 2
    assert isinstance(parsed_scenarios[0], ScenarioConfig)
    
    # Check the first scenario
    assert parsed_scenarios[0].name == "Workday"
    assert parsed_scenarios[0].start_hour == 19
    assert parsed_scenarios[0].end_hour == 7
    assert parsed_scenarios[0].probability == 0.8

def test_parse_scenarios_invalid_probability_sum():
    """Tests if a ValueError is raised if probabilities do not sum to 1.0."""
    # Probabilities sum to 0.9, which is invalid
    scenario_strings = [
        "Workday:19-07:0.8",
        "Holiday:00-24:0.1" 
    ]
    
    config_manager = ConfigManager()
    
    with pytest.raises(ValueError, match="Probabilities must sum to 1.0"):
        config_manager.parse_scenarios(scenario_strings)
