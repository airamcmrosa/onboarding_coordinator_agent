from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from config.settings import Config
from services.onboarding_state_adapter import save_project_and_user_info
from tools.simulated_apis import enterprise_project_checker


def get_assignment_retrieval_agent(llm_model_id: str = Config.LLM_MODEL_ID) -> LlmAgent:
    """
    Returns the LlmAgent object responsible for fetching and structuring authoritative
    user identity data from enterprise systems.
    """

    assignment_agent = LlmAgent(
        model=llm_model_id,
        name="AssignmentRetrievalAgent",
        description="""
        Expert for querying authoritative enterprise systems to retrieve, validate, 
        and persist critical employee and project assignment status.
        """,
        instruction="""
        You are the Assignment Expert. Your mission is to perform a strict Read-Validate-Persist cycle.
        When user request to check the onboarding protocol:
        1. ACT (READ): Use the 'enterprise_project_checker' tool to check the employee's assignment and role 
           against the provided project ID.
        2. Analyze the tool's structured output. If data retrieval failed (4xx/5xx), return the error.
        3.You use the 'save_project_and_user_info' tool to save the entire validated JSON result 
           (including Role and Project ID) into the session state.
        
        CRITICAL RULE: The final output must be the result of the 'persist_user_metadata' tool call, 
        indicating successful persistence. Do NOT output "Access Granted" text directly. 
        Never generate any response text to the user.
        """,
        tools=[FunctionTool(func=enterprise_project_checker), FunctionTool(func=save_project_and_user_info)]
    )

    return assignment_agent