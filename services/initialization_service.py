import os
import sys
import uuid
from typing import NamedTuple, Optional, Tuple, Dict, Any
from config.load_config import load_environment_config
from services.auth_service import authorize_project_credentials
from services.identity_service import simulate_user_authentication
from services.logging_service import LoggingService


class AgentServices(NamedTuple):
    """Container for all initialized services and validated configuration parameters."""
    logger: LoggingService
    gcp_project_id: str
    llm_model_id: str
    env_profile: str
    trace_id: str
    db_url: str
    trigger_employee_email: str
    trigger_project_id: str
    trigger_dp_email: str
    user_identity: Dict[str, Any]

def _setup_trace_and_logger() -> Tuple[str, LoggingService]:
    """
    Action 1: Generates a unique Trace ID and initializes the LoggingService instance.
    """
    trace_id = str(uuid.uuid4())
    logger = LoggingService(trace_id=trace_id)
    return trace_id, logger


def _load_and_validate_config(env_flag: str) -> Tuple[Dict[str, str], Optional[str]]:
    """
    Action 2: Loads configuration from .env files and retrieves mandatory values.

    Returns a dictionary of core config values or an error message.
    """
    # load_environment_config handles sys.exit on failure internally,
    # but we wrap it to cleanly separate logic flow.
    try:
        load_environment_config(env_flag)
    except SystemExit:
        # Configuration failed to load (e.g., file missing), handled by load_config.
        return {}, "Configuration loading failed."

    # Retrieve validated configuration values from os.environ
    config_values = {
        "trigger_employee_email": os.environ["TRIGGER_EMPLOYEE_EMAIL"],
        "trigger_project_id": os.environ["TRIGGER_PROJECT_ID"],
        "trigger_dp_email": os.environ["TRIGGER_EMPLOYEE_DELIVERY_PRINCIPAL_EMAIL"],
        "gcp_project_id": os.environ["GCP_PROJECT_ID"],
        "llm_model_id": os.environ["LLM_MODEL_ID"],
        "env_profile": os.environ["ENV_PROFILE"],
        "db_url": os.environ["DATABASE_URL"],
    }
    return config_values, None


def _check_authentication_status(config: Dict[str, str], logger: LoggingService) -> Optional[str]:
    """
    Action 3: Executes the critical authentication check.

    Returns an error message on failure, or None on success.
    """
    auth_success, error_message = authorize_project_credentials(
        project_id=config["gcp_project_id"],
        logger=logger,
        env_profile=config["env_profile"]
    )

    if not auth_success:
        return f"Authentication check failed: {error_message}"

    return None

def _get_mission_and_identity_context(
        logger: LoggingService,
        trigger_employee_email: str,
        project_id: str,
        dp_email: str
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Action: Retrieves authenticated user identity and mission context.

    Returns: (user_identity_dict, mission_context_dict)
    """

    try:
        # A. Authentication and Identity Deduction (Simulation of SSO data enrichment)
        user_identity = simulate_user_authentication(trigger_employee_email)

        logger.info("User Authenticated and Identity Retrieved.",
                    context={"user_name": user_identity['display_name'],
                             "role": user_identity.get('role', 'N/A'),
                             "target_project": project_id})

        # B. Structuring the final mission context for the Coordinator Agent
        mission_context = {
            "employee_email": trigger_employee_email,
            "project_id": project_id,
            "delivery_principal_email": dp_email
        }

        return user_identity, mission_context

    except Exception as e:
        raise RuntimeError("Context initialization failed.") from e

def _execute_initialization_flow(env: str, trace_id: str, logger: LoggingService) -> Tuple[Optional[AgentServices], Optional[str]]:
    """
    Orchestrates the sequence of setup actions and packages the successful result.
    """
    logger.info("Starting initialization sequence.")

    # 1. Load Config and Validate
    config_values, config_error = _load_and_validate_config(env)
    if config_error:
        # NOTE: Config loading calls sys.exit internally, so this error branch is mainly for clarity.
        return None, config_error

    logger.info(f"Configuration loaded successfully in {config_values['env_profile']} mode.")

    try:
        user_identity, mission_context = _get_mission_and_identity_context(
            logger=logger,
            trigger_employee_email=config_values["trigger_employee_email"],
            project_id=config_values["trigger_project_id"],
            dp_email=config_values["trigger_dp_email"]
        )
    except RuntimeError as e:
        return None, str(e)

    # 2. Check Authentication
    auth_error = _check_authentication_status(config_values, logger)
    if auth_error:
        return None, auth_error

    # 3. Package and Return Services on Success
    logger.info("Application environment initialized successfully. Authentication check passed.")

    services = AgentServices(
        logger=logger,
        gcp_project_id=config_values["gcp_project_id"],
        llm_model_id=config_values["llm_model_id"],
        env_profile=config_values["env_profile"],
        trace_id=trace_id,
        db_url=config_values["db_url"],
        trigger_employee_email=mission_context["employee_email"],
        trigger_project_id=mission_context["project_id"],
        trigger_dp_email=mission_context["delivery_principal_email"],
        user_identity=user_identity
    )
    return services, None


# ----------------------------------------------------------------------
# 3. CONTROL MAIN INITIALIZATION LOGIC (Public Entry Point)
# ----------------------------------------------------------------------

def initialize_application_services(env_flag: str) -> AgentServices:
    """
    Public entry point for mandatory startup processes.
    Executes the initialization flow and handles system exit on critical failure.
    """

    # 1. Setup Logger and Trace ID FIRST (to capture all subsequent events)
    trace_id, logger = _setup_trace_and_logger()

    # 2. Execute the sequence
    services, error_message = _execute_initialization_flow(env_flag, trace_id, logger)

    # 3. Handle Critical Failure (sys.exit)
    if services is None:
        logger.critical_exception(
            "FATAL: Application startup aborted due to critical initialization failure.",
            ValueError(error_message) if error_message else RuntimeError("Unknown initialization error")
        )
        sys.exit(1)

    return services