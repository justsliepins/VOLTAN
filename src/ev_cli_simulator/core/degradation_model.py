import math

class DegradationModel:
    """
    Models the monetary cost of battery wear and tear based on scientific principles.

    This class encapsulates different degradation mechanisms, such as SEI film
    growth, calendar ageing, and cyclic ageing.
    """
    def __init__(self, initial_cost: float = 6.088, decay_rate: float = 0.013):
        """
        Initializes the degradation model with calibrated parameters for SEI growth.

        Args:
            initial_cost (float): The monetary cost (€) of SEI degradation
                                  for the first cycle. This value is derived from
                                  academic research.
            decay_rate (float): The exponential decay rate for SEI cost, also
                                calibrated based on research data.

        Note:
            For a full derivation of these default values, see the project's
            documentation on degradation modeling.
        """
        self.initial_cost = initial_cost
        self.decay_rate = decay_rate

    def get_sei_cost(self, cycle_number: int) -> float:
        """
        Calculates the SEI (Solid Electrolyte Interphase) degradation cost for a
        given cycle using an exponential decay model.

        This cost is highest at the beginning of a battery's life and diminishes
        as a protective layer is formed.

        Args:
            cycle_number (int): The current cycle number of the battery (starting from 1).

        Returns:
            float: The calculated degradation cost in euros (€) for the given cycle.
        """
        if cycle_number < 1:
            # Ensure cycle number is valid to avoid mathematical errors
            return self.initial_cost

        # Formula: cost = initial_cost * e^(-decay_rate * (cycle - 1))
        # (cycle_number - 1) is used because the decay starts after the first cycle.
        cost = self.initial_cost * math.exp(-self.decay_rate * (cycle_number - 1))
        return cost