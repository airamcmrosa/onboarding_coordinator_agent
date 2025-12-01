from typing import Final, Optional

class Config:
    """
    Passive container class for all application settings.
    Values are assigned ONLY after environment loading is successful in main.py.
    This avoids fatal errors during the Python import phase.
    """
    # --- TRIGGER CONTEXT/MISSION INPUTS ---
    TRIGGER_EMPLOYEE_EMAIL: Final[Optional[str]] = None
    TRIGGER_PROJECT_ID: Final[Optional[str]] = None
    TRIGGER_EMPLOYEE_DELIVERY_PRINCIPAL_EMAIL: Final[Optional[str]] = None

    # Core Settings (Final values will be assigned later)
    GCP_PROJECT_ID: Final[Optional[str]] = None
    LLM_MODEL_ID: Final[Optional[str]] = None
    ENV_PROFILE: Final[Optional[str]] = None

    # Agent Constants
    GCHAT_SA_ID: Final[Optional[str]] = None
    ROOT_AGENT_NAME: Final[str] = "OnboardingCoordinatorAgent"
    CRITIC_AGENT_NAME: Final[str] = "OnboardingCriticAgent"

    @staticmethod
    def is_test_mode() -> bool:
        """Returns True if the ENV_PROFILE indicates the deterministic testing environment."""
        return Config.ENV_PROFILE == "test"

    @staticmethod
    def is_dev_mode() -> bool:
        """Returns True if the ENV_PROFILE indicates the real development environment."""
        return Config.ENV_PROFILE == "dev"