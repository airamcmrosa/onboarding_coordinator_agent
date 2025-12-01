from typing import Optional, Tuple
from google.auth import default as google_auth_default
from services.logging_service import LoggingService

def authorize_project_credentials(
        project_id: str,
        logger: LoggingService,
        env_profile: str
) -> Tuple[bool, Optional[str]]:
    """
    Service layer function to authorize the application against Google Cloud APIs.
    Authentication mode (Mock vs. Real ADC) is determined by the env_profile value.
    """
    # Logs the start of the check, including the central control flag (env_profile).
    logger.info("Starting project credentials authorization check.", context={"project_id": project_id, "profile": env_profile})

    # 1. TEST PROFILE LOGIC (MOCKING)
    # The 'test' profile mandates deterministic, mocked behavior for unit tests.
    if env_profile == "test":
        # Uses the env_profile as the explicit mode context.
        logger.info("Authorization mocked successfully for testing.", context={"mode": env_profile})
        return True, None

    # 2. DEVELOPMENT/PRODUCTION LOGIC (REAL ADC)
    try:
        # Attempts to load real credentials via Application Default Credentials (ADC).
        credentials, loaded_project_id = google_auth_default(scopes=["https://www.googleapis.com/auth/cloud-platform"])

        if credentials:
            # Logs success with the loaded project ID.
            logger.info("ADC Loaded successfully. Proceeding with real execution.", context={"loaded_project_id": loaded_project_id, "mode": env_profile})
            return True, None

        # Logs authentication failure.
        error_msg = "ADC not found. Please run 'gcloud auth application-default login'."
        logger.error(error_msg, context={"mode": env_profile})
        return False, error_msg

    except Exception as e:
        # Uses critical_exception for error tracing.
        logger.critical_exception("FATAL: Automatic ADC loading failed.", e, context={"project_id": project_id, "mode": env_profile})
        return False, f"Automatic ADC loading failed: {e}"