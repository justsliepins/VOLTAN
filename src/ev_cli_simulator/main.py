import os
import random
import pandas as pd
import numpy as np  # Import numpy
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Import all our components
from .cli_parser import parse_args
from .config_manager import ConfigManager, ChargerConfig
from .agent_loader import load_agent
from .data_logger import DataLogger
from .core.battery import Battery
from .core.price_model import PriceModel
from .core.degradation_model import DegradationModel
from .core.cost_calculator import CostCalculator
from .core.simulation_engine import SimulationEngine

# A simple baseline agent for comparison
class DumbAgent:
    def predict(self, obs, charger_config: ChargerConfig, deterministic=True):
        soc = obs[0]
        max_power = max(charger_config.power_levels)
        max_power_index = charger_config.power_levels.index(max_power)
        idle_power_index = charger_config.power_levels.index(0) if 0 in charger_config.power_levels else 0
        action_index = max_power_index if soc < 0.9 else idle_power_index
        return (action_index, None)

def run_simulation_run(config, smart_agent, logger, engine_override=None):
    """Executes a single, full simulation run from start to finish."""
    
    smart_battery = Battery(config['battery_capacity'])
    dumb_battery = Battery(config['battery_capacity'])
    
    latvia_tz = ZoneInfo("Europe/Riga")

    if engine_override:
        smart_engine = dumb_engine = engine_override
    else:
        with open(config['price_path'], 'r') as f:
            price_csv_data = f.read()
        
        price_model = PriceModel(price_csv_data)
        degradation_model = DegradationModel()
        cost_calculator = CostCalculator(price_model, degradation_model)
        smart_engine = SimulationEngine(smart_battery, cost_calculator, 8000)
        dumb_engine = SimulationEngine(dumb_battery, cost_calculator, 8000)

    dumb_agent = DumbAgent()
    
    num_days = int(config['years'] * 365)
    
    smart_kwh_charged = 0
    dumb_kwh_charged = 0
    smart_cycle_count = 1
    dumb_cycle_count = 1

    for day in range(num_days):
        charger = random.choice(config['chargers'])
        
        for step in range(96):
            timestamp = datetime(2025, 1, 1, tzinfo=latvia_tz) + timedelta(days=day, minutes=15*step)
            
            # --- Smart Agent's Turn ---
            # **FIX: Convert the observation tuple to a NumPy array**
            obs = np.array([smart_battery.soc, step], dtype=np.float32)
            action_index, _ = smart_agent.predict(obs)

            if action_index >= len(charger.power_levels):
                action_index = charger.power_levels.index(0) if 0 in charger.power_levels else 0
            
            power_kw = charger.power_levels[action_index]
            power_kw = min(power_kw, config['max_charge_speed'])

            results = smart_engine.run_step(power_kw, 0.25, timestamp, smart_cycle_count)
            logger.log_step(
                run_id=config['run_id'], day=day, agent_type='Smart', 
                charging_scenario=charger.name, power_kw=power_kw,
                **results['costs'], **{'soc': results['final_soc'], 'soh': results['final_soh']}
            )
            
            if power_kw > 0:
                smart_kwh_charged += power_kw * 0.25
            if smart_kwh_charged >= config['battery_capacity']:
                smart_cycle_count += 1
                smart_kwh_charged = 0

            # --- Dumb Agent's Turn ---
            # **FIX: Convert the observation tuple to a NumPy array**
            obs = np.array([dumb_battery.soc, step], dtype=np.float32)
            action_index, _ = dumb_agent.predict(obs, charger)
            
            power_kw = charger.power_levels[action_index]
            power_kw = min(power_kw, config['max_charge_speed'])

            results = dumb_engine.run_step(power_kw, 0.25, timestamp, dumb_cycle_count)
            logger.log_step(
                run_id=config['run_id'], day=day, agent_type='Dumb', 
                charging_scenario=charger.name, power_kw=power_kw,
                **results['costs'], **{'soc': results['final_soc'], 'soh': results['final_soh']}
            )

            if power_kw > 0:
                dumb_kwh_charged += power_kw * 0.25
            if dumb_kwh_charged >= config['battery_capacity']:
                dumb_cycle_count += 1
                dumb_kwh_charged = 0

def main():
    """Main entry point for the CLI application."""
    raw_args = parse_args()
    
    config_manager = ConfigManager()
    chargers = config_manager.parse_chargers(raw_args.chargers)
    
    if not os.path.exists(raw_args.agent_path):
        print(f"Error: Agent file not found at {raw_args.agent_path}")
        return

    if not hasattr(raw_args, 'price_path') or not os.path.exists(raw_args.price_path):
        print(f"Error: Price data file not found. Please provide a valid path using --price-path.")
        return

    smart_agent = load_agent(raw_args.agent_path)
    
    full_log = DataLogger()

    for i in range(raw_args.runs):
        print(f"--- Starting Simulation Run {i+1} of {raw_args.runs} ---")
        config = {
            'run_id': i + 1,
            'years': raw_args.years,
            'battery_capacity': raw_args.battery_capacity,
            'max_charge_speed': raw_args.max_charge_speed,
            'chargers': chargers,
            'price_path': raw_args.price_path
        }
        run_simulation_run(config, smart_agent, full_log)

    print("\n--- All simulations complete ---")
    
    df = full_log.get_dataframe()
    
    output_dir = os.path.dirname(raw_args.output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    df.to_csv(raw_args.output_path, index=False)
    print(f"Results saved to {raw_args.output_path}")


if __name__ == "__main__":
    main()
