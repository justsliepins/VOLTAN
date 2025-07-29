import pytest
from src.ev_cli_simulator.cli_parser import parse_args

def test_parse_args():
    """Tests if all command-line arguments are parsed correctly."""
    cli_input = [
        '--price-path', 'data/prices.csv',
        '--years', '8',
        '--runs', '10',
        '--battery-capacity', '77.0',
        '--max-charge-speed', '50.0',
        '--start-soc', '0.3',
        '--soc-target', '0.8',
        # The new, simplified charger argument
        '--charger-power-levels', '[-11,-7.5,0,7.5,11]',
        # The new multi-agent argument
        '--agents', 'AgentV1:path/to/agent1.zip', 'AgentV2:path/to/agent2.zip', 'DumbAgent:baseline',
        '--scenarios', 'Workday:19-07:0.8', 'Holiday:00-24:0.2',
        '--output-path', 'results/'
    ]

    args = parse_args(cli_input)

    # Assertions for all arguments
    assert args.price_path == 'data/prices.csv'
    assert args.years == 8
    assert args.runs == 10
    assert args.battery_capacity == 77.0
    assert args.max_charge_speed == 50.0
    assert args.start_soc == 0.3
    assert args.soc_target == 0.8
    assert args.charger_power_levels == '[-11,-7.5,0,7.5,11]'
    # Assert the new multi-agent argument is parsed correctly
    assert len(args.agents) == 3
    assert args.agents[0] == 'AgentV1:path/to/agent1.zip'
    assert args.agents[2] == 'DumbAgent:baseline'
    assert len(args.scenarios) == 2
    assert args.output_path == 'results/'