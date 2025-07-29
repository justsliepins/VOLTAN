import json
from dataclasses import dataclass
from typing import List

@dataclass
class ChargerConfig:
    """A structured representation of a charger's configuration."""
    name: str
    power_levels: List[int]
    start_hour: int
    end_hour: int

class ConfigManager:
    """
    Handles parsing and validation of command-line arguments into a structured
    configuration for the simulation.
    """
    def parse_chargers(self, charger_strings: List[str]) -> List[ChargerConfig]:
        """
        Parses a list of raw charger definition strings into a list of
        structured ChargerConfig objects.

        Args:
            charger_strings (List[str]): A list of strings from the command line,
                                         e.g., ['Home:[-6,0,6]:19-07'].

        Returns:
            List[ChargerConfig]: A list of validated ChargerConfig objects.
        
        Raises:
            ValueError: If a charger string has an invalid format.
        """
        parsed_chargers = []
        for charger_str in charger_strings:
            try:
                # 1. Split the main parts by the colon delimiter
                name, power_str, time_str = charger_str.split(':')

                # 2. Parse the power levels using json.loads for safety and simplicity
                power_levels = json.loads(power_str)

                # 3. Parse the time window
                start_hour_str, end_hour_str = time_str.split('-')
                start_hour = int(start_hour_str)
                end_hour = int(end_hour_str)

                # 4. Create the structured dataclass object
                config = ChargerConfig(
                    name=name,
                    power_levels=power_levels,
                    start_hour=start_hour,
                    end_hour=end_hour
                )
                parsed_chargers.append(config)

            except (ValueError, json.JSONDecodeError) as e:
                # Catch errors from incorrect splitting (ValueError) or bad JSON (JSONDecodeError)
                raise ValueError(f"Invalid charger format for string: '{charger_str}'. "
                                 f"Expected 'Name:[p1,p2]:start-end'. Error: {e}")
        
        return parsed_chargers