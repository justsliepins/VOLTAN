from datetime import datetime
from .battery import Battery
from .cost_calculator import CostCalculator

class SimulationEngine:
    """
    Orchestrates the entire simulation for a single time step.

    This class acts as the "conductor," using the other core models to
    calculate the consequences of a charging action and update the system state.
    """
    def __init__(self, battery: Battery, cost_calculator: CostCalculator, battery_eol_cost: float):
        """
        Initializes the SimulationEngine.

        Args:
            battery (Battery): An instance of the Battery model.
            cost_calculator (CostCalculator): An instance of the CostCalculator.
            battery_eol_cost (float): The total monetary cost (€) that corresponds
                                      to the battery reaching its End of Life (EOL),
                                      defined as a 20% loss in SOH.
        """
        self.battery = battery
        self.cost_calculator = cost_calculator
        self.battery_eol_cost = battery_eol_cost
        # EOL is defined as a 20% loss of SOH (from 1.0 to 0.8)
        self.EOL_SOH_LOSS = 0.20

    def run_step(
        self,
        power_kw: float,
        duration_h: float,
        timestamp: datetime,
        cycle_number: int
    ) -> dict:
        """
        Executes one full time step of the simulation.

        Args:
            power_kw (float): The power applied in kW for this step.
            duration_h (float): The duration of this step in hours.
            timestamp (datetime): The timestamp of the beginning of the step.
            cycle_number (int): The current cycle number of the battery.

        Returns:
            dict: A dictionary containing the detailed results of the step,
                  including costs and the final battery state.
        """
        # Get the state of the battery *before* the step begins
        initial_soc = self.battery.soc
        
        # 1. Calculate all costs for the proposed action
        costs = self.cost_calculator.calculate_step_costs(
            power_kw=power_kw,
            duration_h=duration_h,
            timestamp=timestamp,
            battery_capacity_kwh=self.battery.capacity_kwh,
            soc=initial_soc,
            cycle_number=cycle_number
        )
        total_cost = costs['total_cost']

        # 2. Convert the monetary cost to physical SOH loss
        # The formula is: (cost_of_this_step / total_cost_to_eol) * total_soh_loss_at_eol
        soh_loss = (total_cost / self.battery_eol_cost) * self.EOL_SOH_LOSS

        # 3. Update the battery's state
        self.battery.update_soc(power_kw, duration_h)
        self.battery.degrade(soh_loss)

        # 4. Return a comprehensive result dictionary
        return {
            "costs": costs,
            "final_soc": self.battery.soc,
            "final_soh": self.battery.soh
        }