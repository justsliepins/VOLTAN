import argparse
from typing import List, Optional

def parse_args(args_list: Optional[List[str]] = None):
    """
    Parses command-line arguments for the EV charging simulator.

    This function defines all the user-configurable parameters for a simulation
    run and parses them from the command line.

    Args:
        args_list (Optional[List[str]]): A list of strings representing the
                                         command-line arguments. Used for testing.
                                         If None, arguments are parsed from sys.argv.

    Returns:
        argparse.Namespace: A populated namespace object containing the parsed
                            arguments as attributes.
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
        nargs='+',  # Allows one or more charger definitions
        required=True,
        help="One or more charger definitions in the format 'Name:[p1,p2]:start_hr-end_hr'."
             " Example: 'Home:[-6,0,6]:19-07'"
    )
    parser.add_argument(
        "--output-path",
        type=str,
        required=True,
        help="Directory path where the final CSV data files will be saved."
    )

    # If args_list is provided (during testing), parse from it.
    # Otherwise, argparse automatically parses from the command line (sys.argv).
    return parser.parse_args(args_list)