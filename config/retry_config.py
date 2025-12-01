from typing import List, Final
from google.genai import types

class RetryConfig:
    """
    Configuration container for managing transient error retry policies.
    """

    # Max number of retries
    MAX_RETRIES: Final[int] = 5

    # Initial delay in seconds (seconds unit added for clarity)
    INITIAL_DELAY_SECONDS: Final[float] = 1.0

    # Exponential base multiplier for delay calculation
    EXPONENTIAL_BASE: Final[int] = 7

    # The list of HTTP status codes that should trigger a retry.
    RETRYABLE_STATUS_CODES: Final[List[int]] = [429, 500, 503, 504]


    @classmethod
    def get_http_retry_options(cls) -> types.HttpRetryOptions:
        """
        Creates and returns the concrete HttpRetryOptions object based on validated settings.

        This method must pass arguments that match the types.HttpRetryOptions constructor
        signature (e.g., attempts, initial_delay, exp_base, http_status_codes).
        """
        return types.HttpRetryOptions(
            attempts=cls.MAX_RETRIES,
            initial_delay=cls.INITIAL_DELAY_SECONDS,
            exp_base=cls.EXPONENTIAL_BASE,
            http_status_codes=cls.RETRYABLE_STATUS_CODES
        )

