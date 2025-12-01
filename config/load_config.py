import os
import sys
from dotenv import load_dotenv
from config.required_vars import REQUIRED_VARS

def load_environment_config(env_flag: str):
    """
    Loads environment variables based on the provided flag (e.g., 'dev', 'test', 'prod').
    Validates that all variables declared in REQUIRED_VARS are present after loading.

    This function is critical for Configuration Management and ensuring the application
    starts with the correct configuration set.

    Args:
        env_flag: The environment flag passed via CLI argument.
    """

    # 1. Load the .env file corresponding to the environment flag.
    env_file = f".env.{env_flag}"
    # Constructs the absolute path to the .env file in the config directory.
    env_path = os.path.join(os.path.dirname(__file__), env_file)

    if not os.path.exists(env_path):
        print(f"FATAL: Environment file not found for flag '{env_flag}'. Expected at: {env_path}")
        sys.exit(1)

    # Loads environment variables from the file into the os.environ dictionary.
    load_dotenv(dotenv_path=env_path)
    print(f"Configuration loaded successfully from {env_file}")

    # 2. Validate Required Variables.
    # Checks if any mandatory variables defined in REQUIRED_VARS are missing from os.environ.
    missing_vars = [var for var in REQUIRED_VARS if var not in os.environ]

    if missing_vars:
        print("FATAL: The following required environment variables are missing:")
        for var in missing_vars:
            print(f"  - {var}")
        print("Please check your required_vars.py and the selected .env file.")
        sys.exit(1)

    print("All required variables validated.")