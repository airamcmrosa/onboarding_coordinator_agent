import os
import pytest
from services.auth_service import authorize_project_credentials
from services.logging_service import LoggingService

# --- Configuration Constants ---
TEST_PROJECT_ID = "mock-project-capstone"
TEST_ENV_PROFILE = "test"
DEV_ENV_PROFILE = "dev"
MOCK_TRACE_ID = "test-auth-trace"

# Initialize a logger instance for use in the test functions
# Note: We need a logger instance to call the refactored authorize_project_credentials.
@pytest.fixture(scope="session")
def test_logger():
    """Provides a dedicated LoggingService instance for test use."""
    return LoggingService(trace_id=MOCK_TRACE_ID)


def test_authorization_success_in_test_profile(test_logger, monkeypatch):
    """
    Tests the mandatory 'test' environment profile, which must always return
    successful authorization to proceed with agent logic unit testing (Mock Success).

    This verifies the "Test Profile Logic (Mocking)" branch in the auth_service.
    """
    # Arrange: Set the environment profile to 'test'
    monkeypatch.setenv("ENV_PROFILE", TEST_ENV_PROFILE)

    # Act: Call the authorization service
    success, message = authorize_project_credentials(
        project_id=TEST_PROJECT_ID,
        logger=test_logger,
        env_profile=TEST_ENV_PROFILE # Passes the controlling profile
    )

    # Assert: In the 'test' profile, authorization must be successful.
    assert success is True
    assert message is None


def test_authorization_real_path_failure_no_credentials(test_logger, monkeypatch):
    """
    Tests the real execution path (e.g., 'dev' profile) when NO Google credentials
    are available (simulating an environment where 'gcloud auth login' has NOT been run).

    This forces the execution into the 'try/except' block's failure path.
    """
    # Arrange: Set the environment profile to 'dev' (forcing real ADC path)
    monkeypatch.setenv("ENV_PROFILE", DEV_ENV_PROFILE)

    # IMPORTANT: Mock the google.auth.default call to simulate 'ADC not found'.
    # This prevents the test from succeeding based on the local machine's actual login status.
    def mock_google_auth_default(scopes):
        return None, None # Simulates no credentials found

    # Use monkeypatch to replace the real function with our mock
    monkeypatch.setattr("google.auth.default", mock_google_auth_default)

    # Act: Call the authorization service
    success, message = authorize_project_credentials(
        project_id=TEST_PROJECT_ID,
        logger=test_logger,
        env_profile=DEV_ENV_PROFILE
    )

    # Assert: The authorization must fail in the 'dev' path due to the missing mock credentials.
    assert success is False
    assert "ADC not found" in message or "ADC loading failed" in message


@pytest.mark.skipif(os.environ.get("ENV_PROFILE") != "integration", reason="Requires manual integration environment setup.")
def test_authorization_real_path_success(test_logger):
    """
    Integration Test: Attempts to load real credentials. Should only run if the user
    explicitly runs an 'integration' environment and has run 'gcloud auth login'.
    """
    # Act: Call the authorization service (uses the actual google.auth.default)
    success, message = authorize_project_credentials(
        project_id=os.environ.get("GCP_PROJECT_ID", "default-proj"),
        logger=test_logger,
        env_profile="integration"
    )

    # Assert: We expect the real path to succeed here if credentials are set up correctly.
    assert success is True
    assert message is None