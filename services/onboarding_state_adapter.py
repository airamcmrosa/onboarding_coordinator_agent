from typing import Dict, Any
from google.adk.tools import ToolContext
import json

def save_project_and_user_info(metadata_json: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Persists validated employee and project metadata into the active session state.

    This function acts as a Memory-as-a-Tool writer, ensuring critical onboarding facts
    are persisted to the shared Session Service (e.g., InMemoryService in test mode)
    via session.update_state().

    Args:
        metadata_json: The validated JSON string containing employee and project data.
        tool_context: The execution context provided by the ADK Runner, which holds the active session.

    Returns:
        Confirmation status for the LLM.
    """

    try:
        metadata_dict = json.loads(metadata_json)

        state_to_persist = {
            "app:project_id": metadata_dict.get("assigned_project_id"),
            "user:email": metadata_dict.get("employee_mail"),
            "user:role": metadata_dict.get("employee_role"),
        }

        tool_context.session.update_state(state_to_persist)

        return {"status": 200, "result": "Metadata successfully updated and persisted."}

    except Exception as e:
        return {"status": 500, "isError": True, "message": f"Persistence failed during save: {e}"}