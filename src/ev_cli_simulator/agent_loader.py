from stable_baselines3 import DQN
import os

def load_agent(agent_path: str):
    """
    Loads a trained Stable-Baselines3 agent from a .zip file.

    Args:
        agent_path (str): The file path to the saved agent model.

    Returns:
        A loaded Stable-Baselines3 model object.

    Raises:
        FileNotFoundError: If the file at the specified path does not exist.
    """
    if not os.path.exists(agent_path):
        raise FileNotFoundError(f"Agent model not found at path: {agent_path}")

    # Use the library's built-in load function
    model = DQN.load(agent_path)
    return model