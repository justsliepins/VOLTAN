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
        "--agent-path",
        type=str,
        required=True,
        help="File path to the trained agent's .zip file."
    )
    parser.add_argument(
        "--price-path",
        type=str,
        required=True,
        help="File path to the CSV file containing historical price data."
    )
    parser.add_argument(
        "--years",
        type=int,
        required=True,
        help="Total duration of the simulation in years."
    )
    parser.add_argument(
        "--runs",
        type=int,
        required=True,
        help="Number of independent simulation runs to perform."
    )
    parser.add_argument(
        "--battery-capacity",
        type=float,
        required=True,
        help="EV's battery capacity in kWh."
    )
    parser.add_argument(
        "--max-charge-speed",
        type=float,
        required=True,
        help="The battery's internal maximum charging speed in kW."
    )
    parser.add_argument(
        "--chargers",
        type=str,
        nargs='+',
        required=True,
        help="One or more charger definitions in the format 'Name:[p1,p2]:start_hr-end_hr'."
    )
    parser.add_argument(
        "--scenarios",
        type=str,
        nargs='+',
        required=True,
        help="One or more charging scenarios in the format 'Name:start_hr-end_hr:probability'."
    )
    # **NEW: Added the SOC target argument**
    parser.add_argument(
        "--soc-target",
        type=float,
        required=True,
        help="The target State of Charge (0.0 to 1.0) to be met by the end of the charging window."
    )
    parser.add_argument(
        "--output-path",
        type=str,
        required=True,
        help="Directory path where the final CSV data files will be saved."
    )
    
    return parser.parse_args(args_list)