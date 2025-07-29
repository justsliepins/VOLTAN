class Battery:
    """
    Models the physical state of an EV battery, tracking its state of charge (SOC).
    """
    def __init__(self, capacity_kwh: float, initial_soc: float = 0.0, initial_soh: float =  1.0):
        """
        Initializes the Battery.

        Args:
            capacity_kwh (float): The total energy capacity of the battery in kWh.
            initial_soc (float): The starting state of charge, from 0.0 to 1.0.
        """
        self.capacity_kwh = float(capacity_kwh)
        self.soc = max(0.0, min(1.0, float(initial_soc)))
        self.soh = max(0.0, min(1.0, float(initial_soh)))

    def update_soc(self, power_kw: float, duration_h: float):
        """
        Updates the battery's SOC based on power applied over a duration.

        The final SOC is clamped between 0.0 and 1.0.

        Args:
            power_kw (float): The power applied in kW. Positive for charging,
                              negative for discharging.
            duration_h (float): The duration of the power application in hours.
        """
        energy_kwh = power_kw * duration_h
        soc_delta = energy_kwh / self.capacity_kwh
        new_soc = self.soc + soc_delta
        self.soc = max(0.0, min(1.0, new_soc))

    def degrade(self, soh_loss: float):
        """
        Reduces the battery's SOH by a given amount.

        The final SOH is clamped at 0.0.
        """
        self.soh = max(0.0, self.soh - soh_loss)