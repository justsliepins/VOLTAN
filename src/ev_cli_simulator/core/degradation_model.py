import math
import numpy as np

class DegradationModel:
    """
    Models the monetary cost of battery wear and tear based on scientific principles.

    This class encapsulates different degradation mechanisms, such as SEI film
    growth, calendar ageing, and cyclic ageing.
    """
    def __init__(self, initial_cost: float = 6.088, decay_rate: float = 0.01301):
        """
        Initializes the degradation model with calibrated parameters.
        """
        # Parameters for SEI film growth
        self.initial_cost = initial_cost
        self.decay_rate = decay_rate

        # Data points for non-linear calendar ageing
        self._calendar_soc_points = [0.0, 0.5, 1.0]
        self._calendar_cost_rates = [0.037, 0.092, 0.204] # €/hour

        # Data points for non-linear cyclic ageing
        # Derived from Snipped.txt, Table 3.4 and €8000 EOL cost
        self._cyclic_c_rate_points = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0]
        self._cyclic_cost_per_cycle = [2.0, 2.78, 4.0, 6.4, 9.14, 10.67] # €/full cycle

    def get_sei_cost(self, cycle_number: int) -> float:
        """
        Calculates the SEI degradation cost for a given cycle.
        """
        if cycle_number < 1:
            return self.initial_cost
        cost = self.initial_cost * math.exp(-self.decay_rate * (cycle_number - 1))
        return cost

    def get_calendar_ageing_cost(self, soc: float, duration_h: float) -> float:
        """
        Calculates calendar ageing cost based on SOC and time.
        """
        current_hourly_rate = np.interp(
            soc, self._calendar_soc_points, self._calendar_cost_rates
        )
        return current_hourly_rate * duration_h

    def get_cyclic_ageing_cost(self, c_rate: float, cycle_portion: float) -> float:
        """
        Calculates cyclic ageing cost based on C-rate and the fraction of a
        full charge/discharge cycle completed.

        This cost is higher at higher C-rates (faster charging).

        Args:
            c_rate (float): The C-rate of the charging/discharging action.
            cycle_portion (float): The fraction of a full cycle completed
                                   (e.g., 0.1 for 10% of the battery's capacity).

        Returns:
            float: The calculated cyclic ageing cost in euros (€).
        """
        # Interpolate to find the cost for one full cycle at the given C-rate
        cost_per_full_cycle = np.interp(
            c_rate, self._cyclic_c_rate_points, self._cyclic_cost_per_cycle
        )

        # The cost for this specific action is proportional to the portion of a cycle used
        return cost_per_full_cycle * cycle_portion