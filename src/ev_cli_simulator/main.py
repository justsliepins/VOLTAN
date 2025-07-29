import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Import all our components
from .cli_parser import parse_args
from .config_manager import ConfigManager, ScenarioConfig, AgentConfig
from .agent_loader import load_agent
from .data_logger import DataLogger
from .core.battery import Battery
from .core.price_model import PriceModel
from .core.degradation_model import DegradationModel
from .core.cost_calculator import CostCalculator
from .core.simulation_engine import SimulationEngine

class DumbAgent:
    """A simple baseline agent that charges at max power if below target SOC."""
    def predict(self, obs, power_levels: list, target_soc: float, deterministic=True):
        soc = obs[0]
        max_power = max(power_levels)
        max_power_index = power_levels.index(max_power)
        idle_power_index = power_levels.index(0) if 0 in power_levels else 0
        action_index = max_power_index if soc < target_soc else idle_power_index
        return (action_index, None)

def run_simulation_run(config, agents_to_run: dict, logger, engine_override=None):
    """Executes a single, full simulation run for multiple agents."""
    
    # Create a separate battery and engine for each agent
    batteries = {name: Battery(config['battery_capacity']) for name in agents_to_run}
    engines = {}
    
    latvia_tz = ZoneInfo("Europe/Riga")

    if engine_override:
        engines = {name: engine_override for name in agents_to_run}
    else:
        with open(config['price_path'], 'r') as f:
            price_csv_data = f.read()
        price_model = PriceModel(price_csv_data)
        degradation_model = DegradationModel()
        cost_calculator = CostCalculator(price_model, degradation_model)
        for name, battery in batteries.items():
            engines[name] = SimulationEngine(battery, cost_calculator, 8000)

    num_days = int(config['years'] * 365)
    scenarios = config['scenarios']
    scenario_choices = [s for s in scenarios]
    scenario_probabilities = [s.probability for s in scenarios]
    
    # Track cycles for each agent
    kwh_charged = {name: 0 for name in agents_to_run}
    cycle_counts = {name: 1 for name in agents_to_run}

    for day in range(num_days):
        daily_scenario = random.choices(scenario_choices, scenario_probabilities)[0]
        
        # Reset SOC for all batteries at the start of the day
        for battery in batteries.values():
            battery.soc = config['start_soc']
        
        daily_log_buffer = []

        for step in range(96):
            timestamp = datetime(2025, 1, 1, tzinfo=latvia_tz) + timedelta(days=day, minutes=15*step)
            current_hour = timestamp.hour

            in_window = False
            start, end = daily_scenario.start_hour, daily_scenario.end_hour
            if start > end:
                if current_hour >= start or current_hour < end: in_window = True
            else:
                if start <= current_hour < end: in_window = True

            if in_window:
                # Loop through each agent and simulate its step
                for name, agent in agents_to_run.items():
                    battery = batteries[name]
                    engine = engines[name]
                    
                    obs = np.array([battery.soc, step], dtype=np.float32)
                    
                    if isinstance(agent, DumbAgent):
                        action_index, _ = agent.predict(obs, config['charger_power_levels'], config['soc_target'])
                    else: # Smart Agent
                        action_index, _ = agent.predict(obs)

                    if action_index >= len(config['charger_power_levels']):
                        action_index = config['charger_power_levels'].index(0) if 0 in config['charger_power_levels'] else 0
                    
                    power_kw = config['charger_power_levels'][action_index]
                    power_kw = min(power_kw, config['max_charge_speed'])

                    results = engine.run_step(power_kw, 0.25, timestamp, cycle_counts[name])
                    
                    daily_log_buffer.append({
                        'agent_type': name, 'timestamp': timestamp,
                        'charging_scenario': daily_scenario.name, 'power_kw': power_kw,
                        **results['costs'], 'soc': results['final_soc'], 'soh': results['final_soh']
                    })
                    
                    if power_kw > 0:
                        kwh_charged[name] += power_kw * 0.25
                    if kwh_charged[name] >= config['battery_capacity']:
                        cycle_counts[name] += 1
                        kwh_charged[name] = 0
        
        # After the day, calculate fulfillment and log all buffered steps
        for entry in daily_log_buffer:
            agent_name = entry['agent_type']
            final_soc_for_day = batteries[agent_name].soc
            fulfillment = final_soc_for_day / config['soc_target']
            logger.log_step(
                run_id=config['run_id'], day=day,
                soc_fulfillment=fulfillment, **entry
            )

def main():
    """Main entry point for the CLI application."""
    raw_args = parse_args()
    
    config_manager = ConfigManager()
    power_levels = config_manager.parse_charger_power_levels(raw_args.charger_power_levels)
    scenarios = config_manager.parse_scenarios(raw_args.scenarios)
    agent_configs = config_manager.parse_agents(raw_args.agents)
    
    # Load all agents into a dictionary
    agents_to_run = {}
    for agent_config in agent_configs:
        if agent_config.path == 'baseline':
            agents_to_run[agent_config.name] = DumbAgent()
        else:
            if not os.path.exists(agent_config.path):
                print(f"Error: Agent file not found at {agent_config.path}")
                return
            agents_to_run[agent_config.name] = load_agent(agent_config.path)
            
    if not hasattr(raw_args, 'price_path') or not os.path.exists(raw_args.price_path):
        print(f"Error: Price data file not found. Please provide a valid path using --price-path.")
        return

    full_log = DataLogger()

    for i in range(raw_args.runs):
        print(f"--- Starting Simulation Run {i+1} of {raw_args.runs} ---")
        config = {
            'run_id': i + 1, 'years': raw_args.years,
            'battery_capacity': raw_args.battery_capacity,
            'max_charge_speed': raw_args.max_charge_speed,
            'start_soc': raw_args.start_soc,
            'soc_target': raw_args.soc_target,
            'charger_power_levels': power_levels,
            'price_path': raw_args.price_path,
            'scenarios': scenarios
        }
        run_simulation_run(config, agents_to_run, full_log)

    print("\n--- All simulations complete ---")
    
    df = full_log.get_dataframe()
    
    output_dir = os.path.dirname(raw_args.output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    df.to_csv(raw_args.output_path, index=False)
    print(f"Results saved to {raw_args.output_path}")


if __name__ == "__main__":
    main()
