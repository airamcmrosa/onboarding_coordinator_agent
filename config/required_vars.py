# A mandatory list of environment variables required for the application to run.
# This list is used by load_config.py to validate that all necessary configurations
# are present for the selected environment (dev, test, prod).
REQUIRED_VARS = [
    # Project IDs and Core Credentials (used by auth_service.py and Google SDK)
    "GCP_PROJECT_ID",

    # Model configuration (impacts cost, latency, and reasoning quality).
    "LLM_MODEL_ID",

    # Fetch the environment to run the project.
    "ENV_PROFILE",

    # --- AGENT SERVICE ACCOUNTS / RESOURCE IDS ---
    # Service Account ID for the Gchat Provisioning Agent (Last Privilege Identity)
    "GCHAT_SA_ID",

    #Database for persisting onboarding protocol as RAG
    "DATABASE_URL",

    # Simulated DP email for simulating SSO login.
    "TRIGGER_EMPLOYEE_DELIVERY_PRINCIPAL_EMAIL",

    "TRIGGER_EMPLOYEE_EMAIL",

    # Project ID used for simulating the target enterprise project.
    "TRIGGER_PROJECT_ID",
]