# 🚀 Enterprise Onboarding Coordinator Agent:

This project is an advanced demonstration of a Level 3 Collaborative Multi-Agent System designed to automate and govern the complex, multi-step process of onboarding new employees (Enterprise Agents track) into enterprise and client-specific IT systems.

The core architecture follows Clean Code (SRP) principles and leverages the Think-Act-Observe loop to ensure security (Least Privilege) and state persistence (Database Session Storage).

#### 1. Setup and Running Locally
This project requires Python 3.10+ (for MCP/ADK compatibility) and Docker/Podman for database setup.

Prerequisites
Python 3.10
+Docker or Podman (Running)
Google Cloud CLI (Required for ADC authentication: 
gcloud auth application-default login)

Step 1: Clone and Environment Setup
Bash# 1. Install dependencies
pip install -r requirements.txt

Before running python main.py dev, you must execute gcloud auth application-default login in your terminal to provide the necessary Google Cloud identity (ADC) for the real API calls.
Bash# 2. Authenticate Google Client Libraries (ADC) for the 'dev' environment

gcloud auth application-default login

#### Step 2: Database and ConfigurationStart PostgreSQL (Database Service): 

This command starts the DB container defined in docker-compose.yml.

Bash
docker compose up -d postgres_db
Configure Environment: Ensure the config/.env.dev and config/.env.test files are present and contain the required variables (especially DATABASE_URL and GCHAT_SA_ID).

---

## Documentation

### Problem Statement
The project aims to automate and orchestrate the complex, multi-step process of enterprise employee onboarding. This involves:
*   **Configuration Management:** Loading and validating environment-specific settings.
*   **Authentication & Authorization:** Verifying user identities and project access credentials.
*   **Protocol Management:** Retrieving existing onboarding protocols or initiating the creation of new ones, which define the specific steps for a given project.
*   **Task Delegation:** Distributing specialized onboarding tasks (e.g., Gchat provisioning, identity verification) to appropriate systems or agents.
*   **Workflow Orchestration:** Managing the overall flow, adapting to different scenarios like existing protocols, new protocol creation, or authorization blocks.

This problem is critical because manual onboarding is often inefficient, prone to human error, and difficult to scale. Automating it ensures consistency, reduces the burden on HR and IT teams, and significantly improves the new employee's initial experience. It also incorporates security best practices through authorization checks and least-privilege access.

### Why agents?
Agents are an ideal solution for this problem due to the inherent complexity and dynamic nature of onboarding:
*   **Orchestration of Complex Workflows:** Onboarding is not a linear process; it involves numerous dependencies and interactions with various systems. A hierarchical multi-agent system, with a central coordinator, can effectively manage and navigate these intricate workflows.
*   **Delegation to Specialists:** Different aspects of onboarding (e.g., Gchat setup, identity verification, project assignment) require distinct expertise. Agents allow for modularity, where each agent acts as a specialist with specific tools and knowledge for its domain.
*   **Adaptability and Decision-Making:** Agents can be designed to interpret the current state (e.g., protocol status, user authorization) and make intelligent decisions on how to proceed, adapting to various scenarios (e.g., "creation mode," "execution mode," "blocked mode").
*   **Tool Use:** Agents are inherently designed to interact with external systems and APIs through defined tools, enabling seamless integration with existing enterprise infrastructure (even if simulated in this prototype).
*   **Human-in-the-Loop (HITL):** The agent architecture can easily incorporate points for human intervention, especially for critical failures or decisions requiring human oversight, as indicated in the coordinator agent's instructions.
*   **Observability:** The structured logging with trace IDs is specifically designed to provide visibility into the distributed actions and thought processes of multiple agents, which is crucial for debugging and monitoring complex agentic systems.

### What you created
The overall architecture is a Python-based multi-agent system designed for enterprise onboarding orchestration:
*   **Main Application (`main.py`):** The application's entry point, responsible for initial setup, environment configuration, and launching the agent `Runner`.
*   **Initialization Service (`services/initialization_service.py`):** Handles core startup processes, including loading configuration, performing initial authentication checks, and setting up the logging infrastructure.
*   **Configuration Module (`config/`):** Manages environment variables (`.env.dev`, `.env.prod`, etc.) and defines required application settings, ensuring a robust and adaptable setup.
*   **Logging Service (`services/logging_service.py`):** Provides a centralized, structured logging mechanism with trace IDs, essential for debugging and monitoring the distributed agent system.
*   **Multi-Agent System (powered by `google.adk`):**
    *   **Coordinator Agent (`agents/coordinator_agent.py`):** The top-level agent. It orchestrates the entire onboarding process, determines the workflow mode (e.g., protocol creation vs. execution), and delegates tasks to specialized sub-agents.
    *   **Assignment Retrieval Agent (`agents/assignment_agent.py`):** A specialized sub-agent focused on querying enterprise systems to retrieve and validate employee assignment status and roles for specific projects.
    *   **Gchat Provisioning Agent (`agents/enterprise_access_agents.py`):** Another specialized sub-agent responsible for automating the process of adding new employees to relevant Google Chat spaces.
*   **Tools (`tools/`):** A collection of simulated APIs (`simulated_apis.py`) that mimic interactions with external enterprise systems (e.g., an enterprise allocation platform, Google Chat API, and a persistent store for onboarding protocols). These tools allow agents to perform actions and retrieve information.
*   **Session Management:** Utilizes an `InMemorySessionService` to maintain the state and context of ongoing onboarding missions.

### Demo
I cannot provide a live, interactive demo. However, based on the code, here's a description of the expected flow when running `python3 main.py dev`:

1.  **Application Startup:** The `main.py` script is executed, loading the development environment configuration.
2.  **Initialization:** The `initialization_service` sets up logging, authenticates the application's credentials, and simulates user authentication (e.g., for "maria.rosa@enterprise.com" for "PROJ-ALPHA").
3.  **Agent System Setup:** The `CoordinatorAgent` and its sub-agents (`AssignmentRetrievalAgent`, `GchatProvisioningAgent`) are instantiated and configured with the appropriate LLM model ID and tools.
4.  **Mission Simulation:** A mission is defined: "Start onboarding for Project ID: PROJ-ALPHA. Employee Email: maria.rosa@enterprise.com."
5.  **Runner Execution:** The `Runner` starts the `CoordinatorAgent` with this mission.
6.  **Coordinator Agent's First Act:** The `CoordinatorAgent`, following its instructions, calls the `check_onboarding_protocol` tool for "PROJ-ALPHA".
7.  **Protocol Found:** Since "PROJ-ALPHA" has a simulated protocol (status 200), the agent enters "EXECUTION MODE."
8.  **Delegation:** The `CoordinatorAgent` then delegates tasks:
    *   It would first delegate to the `AssignmentRetrievalAgent` to verify the user's role and assignment.
    *   Subsequently, it would iterate through the required steps in the protocol and delegate to other agents, such as the `GchatProvisioningAgent`, to add the user to specified Google Chat spaces.
9.  **Mission Completion:** The process continues until all provisioning steps are completed or a critical failure occurs, at which point the "Onboarding Mission simulation completed" message is logged.

### The Build
*   **Language:** Python
*   **Agent Framework:** Google Agent Development Kit (`google.adk`) for building and managing the multi-agent system, including `LlmAgent`, `Runner`, `App`, `FunctionTool`, `AgentTool`, and the `Gemini` model integration.
*   **Data Validation:** `pydantic` is used for robust data validation, particularly for agent configurations and tool inputs/outputs.
*   **Environment Management:** `python-dotenv` for loading environment variables from `.env` files.
*   **Logging:** Python's standard `logging` library, configured for structured output.
*   **Development Environment:** Developed on a local machine (macOS) using a Python virtual environment (`.venv`) for dependency isolation.
*   **Simulated Services:** Custom Python modules (`tools/simulated_apis.py`) to mock external API interactions, enabling deterministic testing and development without live system dependencies.

### If I had more time, this is what I'd do
*   **Implement Real API Integrations:** Replace the simulated APIs in `tools/simulated_apis.py` with actual integrations to enterprise systems (e.g., Google Cloud APIs, HRIS, identity providers, CRM).
*   **Persistent Database for Protocols & State:** Implement a real database (e.g., PostgreSQL, Firestore) to store onboarding protocols, agent session states, and audit logs, moving beyond in-memory or simulated storage.
*   **Enhanced Error Handling and Resilience:** Develop more sophisticated error handling, including exponential backoff, circuit breakers, and dead-letter queues for external API calls, to make the system more robust.
*   **Asynchronous Task Processing:** For long-running provisioning tasks, implement asynchronous processing (e.g., using Celery with a message broker) to improve scalability and responsiveness.
*   **User Interface (UI):** Create a web-based dashboard or UI to provide real-time monitoring of onboarding progress, allow for manual approvals or interventions, and offer a more intuitive user experience.
*   **More Specialized Agents:** Develop additional specialized agents for other common onboarding tasks, such as software license provisioning, access management for various systems, or HR system updates.
*   **Comprehensive Testing Suite:** Expand unit, integration, and end-to-end tests to cover a wider range of scenarios, including edge cases, failure conditions, and security vulnerabilities.
*   **Advanced Observability:** Integrate with a dedicated observability platform (e.g., Google Cloud Operations Suite, OpenTelemetry) for advanced tracing, metrics, and centralized logging in production.
*   **Security Hardening:** Further refine security aspects, including granular access control for agents, secure credential management, and regular security audits.
*   **Dynamic Tool Discovery and Registration:** Explore mechanisms for agents to dynamically discover and register new tools or services as they become available, enhancing system flexibility.
*   **Advanced Agent Capabilities:** Implement capabilities for agents to learn from past onboarding experiences, self-correct their plans, and continuously improve the efficiency and accuracy of the process.