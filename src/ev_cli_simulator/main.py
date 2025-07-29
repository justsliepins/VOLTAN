import os
import random
import pandas as pd
from datetime import datetime, timedelta

# Import all our components
from .cli_parser import parse_args
from .config_manager import ConfigManager
from .agent_loader import load_agent
from .data_logger import DataLogger
from .core.battery import Battery
from .core.price_model import PriceModel
from .core.degradation_model import DegradationModel
from .core.cost_calculator import CostCalculator
from .core.simulation_engine import SimulationEngine

# A simple baseline agent for comparison
class DumbAgent:
    def predict(self, obs, deterministic=True):
        soc = obs[0]
        # Logic: if not 90% full, charge at max power. Otherwise, idle.
        # Assumes max power is the last action, idle is in the middle.
        # This needs to be smarter if action spaces change.
        return (6, None) if soc < 0.9 else (3, None)

def run_simulation_run(config, smart_agent, logger, engine_override=None):
    """Executes a single, full simulation run from start to finish."""
    
    # Setup for this specific run
    # This ensures each run is independent
    smart_battery = Battery(config['battery_capacity'])
    dumb_battery = Battery(config['battery_capacity'])
    
    # The simulation core (can be overridden for testing)
    if engine_override:
        smart_engine = dumb_engine = engine_override
    else:
        # In a real scenario, you'd load a real PriceModel here
        # For now, we create a dummy one.
        csv_data = "timestamp,price_eur_per_kwh\n" + "\n".join([f"{datetime(2025,1,1,h).isoformat()}Z,0.15" for h in range(24)])
        price_model = PriceModel(csv_data)
        degradation_model = DegradationModel()
        cost_calculator = CostCalculator(price_model, degradation_model)
        smart_engine = SimulationEngine(smart_battery, cost_calculator, 8000)
        dumb_engine = SimulationEngine(dumb_battery, cost_calculator, 8000)

    dumb_agent = DumbAgent()
    
    num_days = int(config['years'] * 365)
    
    for day in range(num_days):
        # Randomly select a charger scenario for the day
        charger = random.choice(config['chargers'])
        
        # Simulate 96 steps (15-min intervals) for the day
        for step in range(96):
            timestamp = datetime(2025, 1, 1) + timedelta(days=day, minutes=15*step)
            
            # --- Smart Agent's Turn ---
            obs = (smart_battery.soc, step)
            action, _ = smart_agent.predict(obs)
            # TODO: Map action to power_kw based on selected charger
            power_kw = action * 2 # Simplified mapping
            
            # Cap power by charger and battery limits
            power_kw = min(power_kw, config['max_charge_speed'])

            results = smart_engine.run_step(power_kw, 0.25, timestamp, day // 7) # Approx cycle
            logger.log_step(run_id=config['run_id'], day=day, agent_type='Smart', **results)

            # --- Dumb Agent's Turn ---
            obs = (dumb_battery.soc, step)
            action, _ = dumb_agent.predict(obs)
            power_kw = action * 2 # Simplified mapping
            power_kw = min(power_kw, config['max_charge_speed'])

            results = dumb_engine.run_step(power_kw, 0.25, timestamp, day // 7)
            logger.log_step(run_id=config['run_id'], day=day, agent_type='Dumb', **results)


def main():
    """Main entry point for the CLI application."""
    raw_args = parse_args()
    
    config_manager = ConfigManager()
    chargers = config_manager.parse_chargers(raw_args.chargers)
    
    smart_agent = load_agent(raw_args.agent_path)
    
    full_log = DataLogger()

    for i in range(raw_args.runs):
        print(f"--- Starting Simulation Run {i+1} of {raw_args.runs} ---")
        config = {
            'run_id': i + 1,
            'years': raw_args.years,
            'battery_capacity': raw_args.battery_capacity,
            'max_charge_speed': raw_args.max_charge_speed,
            'chargers': chargers
        }
        run_simulation_run(config, smart_agent, full_log)

    print("\n--- All simulations complete ---")
    
    # Save results
    df = full_log.get_dataframe()
    os.makedirs(os.path.dirname(raw_args.output_path), exist_ok=True)
    df.to_csv(raw_args.output_path, index=False)
    print(f"Results saved to {raw_args.output_path}")


if __name__ == "__main__":
    main()