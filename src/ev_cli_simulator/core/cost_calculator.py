from datetime import datetime
from .price_model import PriceModel
from .degradation_model import DegradationModel

class CostCalculator:
    """
    Orchestrates various models to calculate all costs associated with a
    single charging/discharging step.
    """
    def __init__(self, price_model: PriceModel, degradation_model: DegradationModel):
        """
        Initializes the CostCalculator with the necessary subordinate models.

        Args:
            price_model (PriceModel): An instance of the PriceModel.
            degradation_model (DegradationModel): An instance of the DegradationModel.
        """
        self.price_model = price_model
        self.degradation_model = degradation_model

    def calculate_step_costs(
        self,
        power_kw: float,
        duration_h: float,
        timestamp: datetime,
        battery_capacity_kwh: float,
        soc: float,
        cycle_number: int
    ) -> dict:
        """
        Calculates all cost components for a single time step.

        Args:
            power_kw (float): The power applied in kW.
            duration_h (float): The duration of the step in hours.
            timestamp (datetime): The timestamp of the step.
            battery_capacity_kwh (float): The total capacity of the battery.
            soc (float): The battery's state of charge at the beginning of the step.
            cycle_number (int): The current cycle number of the battery.

        Returns:
            dict: A dictionary containing all individual costs and the total cost.
        """
        # 1. Calculate Electricity Cost
        price = self.price_model.get_price(timestamp)
        if price is None:
            # Handle cases where price data might be missing
            raise ValueError(f"Price not found for timestamp: {timestamp}")
        
        energy_kwh = power_kw * duration_h
        electricity_cost = energy_kwh * price

        # For degradation, only positive power (charging) should incur cost
        if power_kw <= 0:
            calendar_cost = self.degradation_model.get_calendar_ageing_cost(soc, duration_h)
            cyclic_cost = 0.0 # No cyclic cost for discharging or idling
        else:
            # 2. Calculate Calendar Ageing Cost
            calendar_cost = self.degradation_model.get_calendar_ageing_cost(soc, duration_h)

            # 3. Calculate Cyclic Ageing Cost
            c_rate = power_kw / battery_capacity_kwh
            cycle_portion = energy_kwh / battery_capacity_kwh
            cyclic_cost = self.degradation_model.get_cyclic_ageing_cost(c_rate, cycle_portion)

        # 4. Sum the costs
        total_cost = electricity_cost + calendar_cost + cyclic_cost

        return {
            "electricity_cost": electricity_cost,
            "calendar_cost": calendar_cost,
            "cyclic_cost": cyclic_cost,
            "total_cost": total_cost,
        }