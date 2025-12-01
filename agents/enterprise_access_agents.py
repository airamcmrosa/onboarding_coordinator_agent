from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool, FunctionTool
from google.adk.models import Gemini
from config.retry_config import RetryConfig
from config.settings import Config
from tools.api_connectors import gchat_add_member
from tools.simulated_apis import gchat_add_member_mock, read_gchat_spaces_list


# ----------------------------------------------------------------------
# 1. HELPER FUNCTION: Tool Function Selector (SRP: Environment Control)
# ----------------------------------------------------------------------

def _get_gchat_base_function():
    """
    Selects the underlying tool function (Mock or Prod) based on the ENV_PROFILE.
    This manages the environment separation for deterministic testing (TDD).
    """
    if Config.ENV_PROFILE == "test":
        return gchat_add_member_mock
    else:
        return gchat_add_member


# ----------------------------------------------------------------------
# 2. HELPER FUNCTION: Tool Factory (SRP: Security Binding and Metadata)
# ----------------------------------------------------------------------

def _create_gchat_tool() -> FunctionTool:
    """
    Factory method that creates the Gchat tool, binding the correct base function
    and the least-privilege Service Account ID via a closure.
    """
    # Access the authorized SA ID from the passive Config class.
    authorized_sa = Config.GCHAT_SA_ID
    base_tool_function = _get_gchat_base_function()

    # Closure Function: Wraps the base function to inject the security constraint.
    def bound_gchat_add_member(space_name: str, employee_email: str, service_account_id: str):
        """
        Calls the underlying Gchat service function, injecting the known authorized SA ID
        for validation against the LLM's suggested service_account_id.
        """
        # Inject the authorized_sa_id from configuration into the tool call.
        return base_tool_function(
            space_name=space_name,
            employee_email=employee_email,
            service_account_id=service_account_id,
            authorized_sa_id=authorized_sa
        )

    # Tool Metadata Preservation (Essential for LLM Reasoning and Tracing)
    bound_gchat_add_member.__doc__ = base_tool_function.__doc__
    bound_gchat_add_member.__name__ = base_tool_function.__name__

    # Pass the closure function object into the FunctionTool constructor.
    return FunctionTool(bound_gchat_add_member)


# ----------------------------------------------------------------------
# 3. AGENT DEFINITION FACTORY (The final object creator)
# ----------------------------------------------------------------------

def get_gchat_provisioning_agent(llm_model_id: str) -> LlmAgent:
    """
    Returns the configured LlmAgent object for Gchat provisioning.
    This micro-agent executes the two-step provisioning sequence.
    """

    # 1. Create the specialized action and retrieval tool objects
    chat_add_member_tool = _create_gchat_tool()

    # Tool for reading the Onboarding Protocol (Information Retrieval)
    read_spaces_tool = FunctionTool(read_gchat_spaces_list)

    # 2. Configure the model with robustness features
    agent_model = Gemini(model=llm_model_id, retry_options=RetryConfig.get_http_retry_options())

    # 3. Instantiate the LlmAgent Object
    gchat_agent = LlmAgent(
        model=agent_model,
        name="GchatProvisioningAgent",
        description=f"""
        Expert for adding users to Google Chat spaces. You act using the specialized 
        Service Account '{Config.GCHAT_SA_ID}' for least privilege access.
        """,
        instruction=f"""
        You are the Gchat Provisioning Expert. Your mission requires two sequential steps:
        1. ACT: Use the '{read_spaces_tool.name}' tool to retrieve the list of spaces for the project.
        2. ACT/ITERATE: For every space name retrieved, you MUST call the '{chat_add_member_tool.name}' tool 
           to add the new member. You MUST include the Service Account ID '{Config.GCHAT_SA_ID}' in every tool call.
        
        CRITICAL RULE: Never generate any response text to the user. Only use the tools provided.
        """,
        tools=[read_spaces_tool, chat_add_member_tool]
    )

    return gchat_agent