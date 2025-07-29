# In a new file: tests/test_agent_loader.py

import pytest
import os
from stable_baselines3 import DQN
import gymnasium as gym
from src.ev_cli_simulator.agent_loader import load_agent

@pytest.fixture
def dummy_agent_file(tmp_path):
    """
    Creates a temporary, valid SB3 DQN agent file for testing.
    
    tmp_path is a built-in pytest fixture that provides a temporary directory.
    """
    # Create a simple environment for the dummy agent
    env = gym.make("CartPole-v1")
    # Create a dummy model
    model = DQN("MlpPolicy", env)
    # Define the file path inside the temporary directory
    file_path = tmp_path / "dummy_agent.zip"
    # Save the dummy model
    model.save(file_path)
    return file_path

def test_load_agent_success(dummy_agent_file):
    """Tests if a valid agent is loaded correctly."""
    loaded_model = load_agent(dummy_agent_file)
    # Check if the returned object is an instance of the DQN class
    assert isinstance(loaded_model, DQN)

def test_load_agent_file_not_found():
    """Tests if a FileNotFoundError is raised for a non-existent path."""
    invalid_path = "path/to/non_existent_agent.zip"
    with pytest.raises(FileNotFoundError):
        load_agent(invalid_path)