import pytest
from src.ev_cli_simulator.cli_parser import parse_args

def test_parse_args():
    """Tests if all command-line arguments are parsed correctly."""
    # Simulate the command-line input, now including --soc-target
    cli_input = [
        '--agent-path', 'path/to/agent.zip',
        '--years', '8',
        '--runs', '10',
        '--battery-capacity', '77.0',
        '--max-charge-speed', '50.0',
        '--chargers', 'Home:[-6,0,6]:19-07', 'Work:[-11,0,11]:09-17',
        '--output-path', 'results/',
        '--price-path', 'data/prices.csv',
        '--scenarios', 'Workday:19-07:0.8', 'Holiday:00-24:0.2',
        # The new argument to match the updated parser
        '--soc-target', '0.8'
    ]

    args = parse_args(cli_input)

    # Assertions for all arguments
    assert args.agent_path == 'path/to/agent.zip'
    assert args.years == 8
    assert args.runs == 10
    assert args.battery_capacity == 77.0
    assert args.max_charge_speed == 50.0
    assert len(args.chargers) == 2
    assert args.chargers[0] == 'Home:[-6,0,6]:19-07'
    assert args.output_path == 'results/'
    assert args.price_path == 'data/prices.csv'
    assert len(args.scenarios) == 2
    assert args.scenarios[1] == 'Holiday:00-24:0.2'
    # Assertion for the new argument
    assert args.soc_target == 0.8