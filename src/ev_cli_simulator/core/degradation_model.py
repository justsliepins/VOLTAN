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

        # Data points for non-linear calendar ageing, derived from research.
        # X-values: State of Charge (0.0 to 1.0)
        self._calendar_soc_points = [0.0, 0.5, 1.0]
        # Y-values: Corresponding cost in euros per hour (€/h)
        self._calendar_cost_rates = [0.037, 0.092, 0.204]


    def get_sei_cost(self, cycle_number: int) -> float:
        """
        Calculates the SEI degradation cost for a given cycle using an
        exponential decay model.
        """
        if cycle_number < 1:
            return self.initial_cost
        cost = self.initial_cost * math.exp(-self.decay_rate * (cycle_number - 1))
        return cost

    def get_calendar_ageing_cost(self, soc: float, duration_h: float) -> float:
        """
        Calculates calendar ageing cost based on SOC and time using piecewise
        linear interpolation on data from academic research.

        This cost is higher at higher states of charge.

        Args:
            soc (float): The battery's current State of Charge (0.0 to 1.0).
            duration_h (float): The duration in hours for which the cost is calculated.

        Returns:
            float: The calculated calendar ageing cost in euros (€).
        """
        # Use numpy.interp to find the current cost rate for the given SOC.
        # This function handles all interpolation and edge cases cleanly.
        current_hourly_rate = np.interp(
            soc, self._calendar_soc_points, self._calendar_cost_rates
        )

        return current_hourly_rate * duration_h