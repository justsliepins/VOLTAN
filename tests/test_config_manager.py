import pytest
from src.ev_cli_simulator.config_manager import ConfigManager, ChargerConfig

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