import json
import math
from dataclasses import dataclass
from typing import List

# This dataclass is no longer needed as we have a single charger
# @dataclass
# class ChargerConfig: ...

@dataclass
class ScenarioConfig:
    """A structured representation of a daily charging scenario."""
    name: str
    start_hour: int
    end_hour: int
    probability: float

@dataclass
class AgentConfig:
    """A structured representation of an agent to be simulated."""
    name: str
    path: str # Can be a file path or 'baseline'

class ConfigManager:
    """
    Handles parsing and validation of command-line arguments into a structured
    configuration for the simulation.
    """
    def parse_charger_power_levels(self, power_level_string: str) -> List[float]:
        """Parses the charger power levels string into a list of floats."""
        try:
            power_levels = json.loads(power_level_string)
            if not isinstance(power_levels, list):
                raise ValueError("Power levels must be a list.")
            return [float(p) for p in power_levels]
        except (ValueError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid format for charger power levels: '{power_level_string}'. Error: {e}")

    def parse_scenarios(self, scenario_strings: List[str]) -> List[ScenarioConfig]:
        """
        Parses a list of raw scenario definition strings into a list of
        structured ScenarioConfig objects.
        """
        parsed_scenarios = []
        total_prob = 0.0
        for scenario_str in scenario_strings:
            try:
                name, time_str, prob_str = scenario_str.split(':')
                start_hour_str, end_hour_str = time_str.split('-')
                start_hour = int(start_hour_str)
                end_hour = int(end_hour_str)
                probability = float(prob_str)
                total_prob += probability
                config = ScenarioConfig(name, start_hour, end_hour, probability)
                parsed_scenarios.append(config)
            except ValueError as e:
                raise ValueError(f"Invalid scenario format: '{scenario_str}'. Error: {e}")
        
        if not math.isclose(total_prob, 1.0):
            raise ValueError(f"Probabilities must sum to 1.0, but got {total_prob}")
            
        return parsed_scenarios

    def parse_agents(self, agent_strings: List[str]) -> List[AgentConfig]:
        """Parses agent definition strings into a list of AgentConfig objects."""
        parsed_agents = []
        for agent_str in agent_strings:
            try:
                # Split only on the first colon to handle Windows paths correctly
                name, path = agent_str.split(':', 1)
                config = AgentConfig(name=name, path=path)
                parsed_agents.append(config)
            except ValueError:
                raise ValueError(f"Invalid agent format: '{agent_str}'. Expected 'Name:path/to/agent.zip'")
        return parsed_agents
