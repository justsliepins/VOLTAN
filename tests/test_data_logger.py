# In a new file: tests/test_data_logger.py

import pandas as pd
from src.ev_cli_simulator.data_logger import DataLogger

def test_data_logger():
    """
    Tests if the DataLogger correctly logs step data and can export it
    as a pandas DataFrame.
    """
    logger = DataLogger()

    # Log two sample steps
    logger.log_step(
        run_id=1,
        day=1,
        timestamp="2025-01-01T19:00:00Z",
        agent_type="Smart",
        # ... add all other required data points
        soc=0.5,
        soh=0.99
    )
    logger.log_step(
        run_id=1,
        day=1,
        timestamp="2025-01-01T19:15:00Z",
        agent_type="Smart",
        # ...
        soc=0.55,
        soh=0.98
    )

    # Get the final DataFrame
    df = logger.get_dataframe()

    # Assertions
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == [
        "run_id", "day", "timestamp", "agent_type", "soc", "soh"
    ]
    assert df.iloc[0]['soc'] == 0.5
    assert df.iloc[1]['soh'] == 0.98