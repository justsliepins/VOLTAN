import pandas as pd
from typing import List, Dict, Any

class DataLogger:
    """
    Collects and stores detailed data from each step of the simulation.
    """
    def __init__(self):
        """Initializes the DataLogger with an empty list to store log entries."""
        self._log_entries: List[Dict[str, Any]] = []

    def log_step(self, **kwargs):
        """
        Logs a dictionary of data for a single simulation step.

        Args:
            **kwargs: Arbitrary key-value pairs representing the data for one step.
                      These keys should correspond to the desired CSV columns.
        """
        self._log_entries.append(kwargs)

    def get_dataframe(self) -> pd.DataFrame:
        """
        Converts all logged entries into a single pandas DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing all the simulation data,
                          ready for analysis or export.
        """
        if not self._log_entries:
            return pd.DataFrame() # Return an empty DataFrame if no data was logged

        return pd.DataFrame(self._log_entries)