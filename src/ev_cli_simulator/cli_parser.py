import argparse
from typing import List, Optional

def parse_args(args_list: Optional[List[str]] = None):
    """
    Parses command-line arguments for the EV charging simulator.
    """
    parser = argparse.ArgumentParser(
        description="Run a long-term EV charging simulation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # --- Required Arguments ---
    parser.add_argument(
        "--price-path", type=str, required=True,
        help="File path to the CSV file containing historical price data."
    )
    parser.add_argument(
        "--years", type=int, required=True,
        help="Total duration of the simulation in years."
    )
    parser.add_argument(
        "--runs", type=int, required=True,
        help="Number of independent simulation runs to perform."
    )
    parser.add_argument(
        "--battery-capacity", type=float, required=True,
        help="EV's battery capacity in kWh."
    )
    parser.add_argument(
        "--max-charge-speed", type=float, required=True,
        help="The battery's internal maximum charging speed in kW."
    )
    parser.add_argument(
        "--start-soc", type=float, required=True,
        help="The SOC (0.0 to 1.0) the battery starts with each day, simulating driving."
    )
    parser.add_argument(
        "--soc-target", type=float, required=True,
        help="The target SOC (0.0 to 1.0) to be met by the end of the charging window."
    )
    parser.add_argument(
        "--charger-power-levels", type=str, required=True,
        help="A string representing the list of power levels for the single home charger. "
             "Example: '[-11,-7.5,0,7.5,11]'"
    )
    # **NEW: Replaced --agent-path with --agents**
    parser.add_argument(
        "--agents", type=str, nargs='+', required=True,
        help="One or more agent definitions in the format 'Name:path/to/agent.zip'. "
             "Use 'DumbAgent:baseline' for the baseline agent."
    )
    parser.add_argument(
        "--scenarios", type=str, nargs='+', required=True,
        help="One or more charging scenarios in the format 'Name:start_hr-end_hr:probability'."
    )
    parser.add_argument(
        "--output-path", type=str, required=True,
        help="Directory path where the final CSV data files will be saved."
    )
    
    return parser.parse_args(args_list)
