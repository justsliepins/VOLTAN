import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Import all our components
from .cli_parser import parse_args
from .config_manager import ConfigManager, ChargerConfig, ScenarioConfig
from .agent_loader import load_agent
from .data_logger import DataLogger
from .core.battery import Battery
from .core.price_model import PriceModel
from .core.degradation_model import DegradationModel
from .core.cost_calculator import CostCalculator
from .core.simulation_engine import SimulationEngine

# A simple baseline agent for comparison
class DumbAgent:
    def predict(self, obs, charger_config: ChargerConfig, target_soc: float, deterministic=True):
        """
        A simple baseline agent that charges at max power if below target SOC.
        """
        soc = obs[0]
        max_power = max(charger_config.power_levels)
        max_power_index = charger_config.power_levels.index(max_power)
        idle_power_index = charger_config.power_levels.index(0) if 0 in charger_config.power_levels else 0
        # **FIX: Use the dynamic target_soc**
        action_index = max_power_index if soc < target_soc else idle_power_index
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
    
    scenarios = config['scenarios']
    scenario_choices = [s for s in scenarios]
    scenario_probabilities = [s.probability for s in scenarios]
    
    smart_kwh_charged = 0
    dumb_kwh_charged = 0
    smart_cycle_count = 1
    dumb_cycle_count = 1

    for day in range(num_days):
        if not config['chargers']:
            raise ValueError("Configuration error: At least one charger must be provided.")
        charger = random.choice(config['chargers'])
        
        daily_scenario = random.choices(scenario_choices, scenario_probabilities)[0]
        
        # **NEW: Variables to track end-of-window state and daily costs**
        smart_soc_end_of_window = None
        dumb_soc_end_of_window = None
        daily_smart_costs = {}
        daily_dumb_costs = {}

        for step in range(96):
            timestamp = datetime(2025, 1, 1, tzinfo=latvia_tz) + timedelta(days=day, minutes=15*step)
            current_hour = timestamp.hour

            in_window = False
            start, end = daily_scenario.start_hour, daily_scenario.end_hour
            if start > end:
                if current_hour >= start or current_hour < end:
                    in_window = True
            else:
                if start <= current_hour < end:
                    in_window = True

            if in_window:
                # --- Smart Agent's Turn ---
                obs = np.array([smart_battery.soc, step], dtype=np.float32)
                action_index, _ = smart_agent.predict(obs)

                if action_index >= len(charger.power_levels):
                    action_index = charger.power_levels.index(0) if 0 in charger.power_levels else 0
                
                power_kw = charger.power_levels[action_index]
                power_kw = min(power_kw, config['max_charge_speed'])

                results = smart_engine.run_step(power_kw, 0.25, timestamp, smart_cycle_count)
                
                # Accumulate daily costs
                for key, value in results['costs'].items():
                    daily_smart_costs[key] = daily_smart_costs.get(key, 0) + value
                
                if power_kw > 0:
                    smart_kwh_charged += power_kw * 0.25
                if smart_kwh_charged >= config['battery_capacity']:
                    smart_cycle_count += 1
                    smart_kwh_charged = 0

                # --- Dumb Agent's Turn ---
                obs = np.array([dumb_battery.soc, step], dtype=np.float32)
                action_index, _ = dumb_agent.predict(obs, charger, config['soc_target'])
                
                power_kw_dumb = charger.power_levels[action_index]
                power_kw_dumb = min(power_kw_dumb, config['max_charge_speed'])

                results_dumb = dumb_engine.run_step(power_kw_dumb, 0.25, timestamp, dumb_cycle_count)

                for key, value in results_dumb['costs'].items():
                    daily_dumb_costs[key] = daily_dumb_costs.get(key, 0) + value

                if power_kw_dumb > 0:
                    dumb_kwh_charged += power_kw_dumb * 0.25
                if dumb_kwh_charged >= config['battery_capacity']:
                    dumb_cycle_count += 1
                    dumb_kwh_charged = 0
            
            # Capture the SOC at the moment the window closes
            if not in_window and smart_soc_end_of_window is None and step > 0:
                smart_soc_end_of_window = smart_battery.soc
                dumb_soc_end_of_window = dumb_battery.soc
        
        # Log the daily summary
        if smart_soc_end_of_window is None: # Handle cases where window is 24h
            smart_soc_end_of_window = smart_battery.soc
            dumb_soc_end_of_window = dumb_battery.soc
            
        logger.log_step(
            run_id=config['run_id'], 
            day=day, 
            agent_type='Smart', 
            final_soc=smart_soc_end_of_window,
            final_soh=smart_battery.soh,
            soc_fulfillment=smart_soc_end_of_window / config['soc_target'],
            **daily_smart_costs
        )
        logger.log_step(
            run_id=config['run_id'], 
            day=day, 
            agent_type='Dumb', 
            final_soc=dumb_soc_end_of_window,
            final_soh=dumb_battery.soh,
            soc_fulfillment=dumb_soc_end_of_window / config['soc_target'],
            **daily_dumb_costs
        )


def main():
    """Main entry point for the CLI application."""
    raw_args = parse_args()
    
    config_manager = ConfigManager()
    chargers = config_manager.parse_chargers(raw_args.chargers)
    scenarios = config_manager.parse_scenarios(raw_args.scenarios)
    
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
            'price_path': raw_args.price_path,
            'scenarios': scenarios,
            'soc_target': raw_args.soc_target # **NEW: Add soc_target to config**
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