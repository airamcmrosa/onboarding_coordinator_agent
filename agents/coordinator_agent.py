from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools import FunctionTool, AgentTool

from agents.assignment_agent import get_assignment_retrieval_agent
from agents.enterprise_access_agents import get_gchat_provisioning_agent
from config.settings import Config
from config.retry_config import RetryConfig
from tools.simulated_apis import check_onboarding_protocol


def get_coordinator_agents_tools (llm_model_id: str) -> list[AgentTool]:
    """
    Returns a list of all AgentTools available directly to the Coordinator Agent.
    This factory assembles all specialized A2A and Function Tools.
    """
    # NOTE: Assuming placeholder factories are available for instantiation.
    assignment_agent = get_assignment_retrieval_agent(llm_model_id)
    gchat_agent = get_gchat_provisioning_agent(llm_model_id)

    agents_tools = [
        AgentTool(agent=assignment_agent),
        AgentTool(agent=gchat_agent)
    ]

    return agents_tools


def get_coordinator_agent(llm_model_id: str = Config.LLM_MODEL_ID) -> LlmAgent:
    """
    Returns the configured LlmAgent object for the root Onboarding Coordinator.
    This agent orchestrates the entire onboarding process (Level 2: Strategic Problem-Solver).
    """

    agent_model = Gemini(
        model=llm_model_id,
        retry_options=RetryConfig.get_http_retry_options()
    )
    agent_tools = get_coordinator_agents_tools(llm_model_id)

    initial_tools = [FunctionTool(func=check_onboarding_protocol)] + agent_tools

    return LlmAgent(
        model=agent_model,
        name=Config.ROOT_AGENT_NAME,
        description="""
        The Root Agent orchestrating the enterprise employee onboarding process. Your mission is 
        to execute the workflow and maintain a highly informative conversation with the user.
        """,
        instruction=f"""
        You are the Onboarding Coordinator Agent for the Enterprise. Your primary role is to act as a collaborative entity: **guide the employee and execute the necessary provisioning steps.**
        
        Your primary goal is to ensure all provisioning steps from the Onboarding Protocol are executed.

        1. FIRST ACT: Use the 'check_onboarding_protocol' tool, providing the project_id (from the user mission) and the user's authorization status (is_user_authorized_to_create). This Tool handles retrieval (RAG) or creation automatically.
        
        2. OBSERVE: Analyze the status code and the payload returned by the tool.
        
        3. THINK (Workflow Routing and Information Synthesis):
           
           A. EXECUTION MODE (Status 200 - Protocol Found):
              - **THINK:** Acknowledge the successful lookup. Synthesize the 'protocol_version' and the 'required_steps_enterprise' into a brief, informative message for the user.
              - **INSTRUCT USER:** State clearly that the protocol is active and ask the user to confirm starting the process.
              - **NEXT ACT:** Delegate user role verification to the 'IdentityRetrievalAgent' Tool (This step happens ONLY after user confirmation).

           B. CREATION MODE (Status 201 - New Draft Created):
              - **SYNTHESIZE & INSTRUCT:** Inform the user that the Protocol did not exist but that a new draft has been created for them (since they are authorized). Ask the user to define the necessary steps for the new protocol.
              
           C. BLOCKED MODE (Status 403 - Not Authorized / 404 - Not Found):
              - **SYNTHESIZE & INSTRUCT:** Inform the user explicitly that a standard protocol was not found OR they lack the authorization to proceed. Direct them to contact the Delivery Principal or Project Manager.
              
           D. ERROR/FAILURE HANDLING (Status 4xx/5xx):
              - Log the full error output (OBSERVE).
              - Return a sympathetic, informative message to the user about the system failure and advise them to seek human support.
           
        Based on the current mission, output your thought process (THINK) and then your next action (ACT).
        
        **NOTE ON OUTPUT:** You must synthesize complex tool output (like the checklist) into concise, conversational language for the user. You are a collaborative entity, not a technical logging system.
        """,
        tools=initial_tools
    )