# In a new file: tests/test_cli_parser.py

import pytest
from src.ev_cli_simulator.cli_parser import parse_args

def test_parse_args():
    """Tests if the command-line arguments are parsed correctly."""
    # Simulate the command-line input
    cli_input = [
        '--agent-path', 'path/to/agent.zip',
        '--years', '8',
        '--runs', '10',
        '--battery-capacity', '77.0',
        '--max-charge-speed', '50.0',
        '--chargers', 'Home:[-6,0,6]:19-07', 'Work:[-11,0,11]:09-17',
        '--output-path', 'results/'
    ]

    args = parse_args(cli_input)

    assert args.agent_path == 'path/to/agent.zip'
    assert args.years == 8
    assert args.runs == 10
    assert args.battery_capacity == 77.0
    assert args.max_charge_speed == 50.0
    assert len(args.chargers) == 2
    assert args.chargers[0] == 'Home:[-6,0,6]:19-07'
    assert args.output_path == 'results/'