from typing import Dict, Any


def enterprise_project_checker(employee_mail: str, project_id: str) -> Dict[str, Any]:
    """
    Simulates calling the Enterprise Allocation Platform API to check the employee's
    assignment status and role against the requested project ID.

    Args:
        employee_mail: The verified email address of the employee.
        project_id: The project ID the employee is checking in against.

    Returns:
        A structured JSON response detailing the outcome: assigned role, project team,
        and validation status.
    """
    employee_mail_lower = employee_mail.lower()

    ROSTER_ALPHA = [
        {"email": "maria.rosa@enterprise.com", "role": "Developer", "status": "Active"},
        {"email": "alice.manfieldr@enterprise.com", "role": "Project Manager", "status":
            "Active"},
        {"email": "bob.lover@enterprise.com", "role": "UX Designer", "status": "Active"},
    ]

    target_roster = ROSTER_ALPHA if project_id == "PROJ-ALPHA" else []

    assignment_match = next(
        (member for member in target_roster if member["email"] == employee_mail_lower),
        None
    )

    if assignment_match:
        return {
            "status": 200,
            "assignment_valid": True,
            "employee_role": assignment_match["role"],
            "assigned_project_id": project_id,
            "project_roster_count": len(target_roster),
            "message": f"Assignment verified. User is the assigned "
                       f"{assignment_match['role']} for {project_id}.",
            "employee_mail": employee_mail
        }
    else:
        return {
            "status": 401,
            "isError": True,
            "assignment_valid": False,
            "employee_role": "Unassigned",
            "assigned_project_id": "NONE",
            "message": f"Access denied. Employee is not currently assigned to project "
                       f"{project_id} in the Enterprise system.",
            "employee_mail": employee_mail
        }


def check_onboarding_protocol(project_id: str) -> Dict[str, Any]:
    """
    Simulates querying the persistent Onboarding Protocol Artifact (Memory)
    to retrieve the project's status, steps, and overall protocol existence.

    This function is critical for the Agent's initial planning phase (Think It Through).

    Args:
        project_id: The ID of the project whose protocol status is needed.

    Returns:
        A structured JSON response detailing the protocol status and required steps.
    """

    if project_id == "PROJ-ALPHA":
        return {
            "status": 200,
            "protocol_found": True,
            "protocol_version": "v2.1",
            "required_steps_tw": [
                "Gchat Provisioning",
                "Drive Access Setup",
                "Onboarding Checklist Update"
            ],
            "required_steps_client": [
                "Client Azure Account Request",
                "Client Repo Access"
            ],
            "spaces_list": ["spaces/ALPHA-GENERAL", "spaces/ALPHA-DEV"],
            "is_user_authorized_to_create": False,
            "message": "Protocol found and ready for execution."
        }

    if project_id == "PROJ-BETA":
        # Scenario: Protocol not found, but user needs to be authorized to create it (Modo 1)
        return {
            "status": 404,
            "protocol_found": False,
            "protocol_version": "N/A",
            "required_steps_tw": [],
            "required_steps_client": [],
            "spaces_list": [],
            "is_user_authorized_to_create": True,
            "message": "Protocol not found. User needs to initiate creation workflow."
        }

    return {"status": 404, "protocol_found": False, "message": "Project ID not recognized."}

def read_gchat_spaces_list(project_id: str) -> Dict[str, Any]:
    """
    Simulates querying the persistent Onboarding Protocol Artifact (Memory)
    to retrieve the list of required Google Chat space names for a project.

    This tool is critical for the Agent's planning, providing the required
    contextual data to start the execution loop.

    Args:
        project_id: The ID of the project whose spaces are needed.

    Returns:
        A structured dictionary containing the list of space names or an error status.
    """
    response = check_onboarding_protocol(project_id)
    return {
        "status": response["status"],
        "spaces_list": response.get("spaces_list", []),
        "message": response.get("message")
    }

def gchat_add_member_mock(space_name: str, employee_mail: str, service_account_id: str, authorized_sa_id: str) -> Dict[str, Any]:
    """
    Simulates calling the Google Chat API to add a member to a space (MOCK).

    The purpose is to verify the Agent's planning (parameters) and the Service's
    security policy (service_account_id) deterministically.

    Args:
        space_name: The resource name of the Chat space (e.g., 'spaces/AAAAAAAAAAA').
        employee_mail: The email address of the new member (e.g., 'user@thoughtworks.com').
        service_account_id: The ID of the least-privileged Service Account provided by the LLM (for audit).
        authorized_sa_id: The EXPECTED least-privileged Service Account ID from config.

    Returns:
        A structured JSON response with status and resource_name upon success.
    """

    # 1. Security/Authorization Check (MOCK)
    if service_account_id != authorized_sa_id:
        # Simulates a PERMISSION_DENIED (403) due to incorrect identity.
        return {
            "status": 403,
            "isError": True,
            "error_type": "SECURITY_FAILURE",
            "message": f"Authorization Failed: Agent identity mismatch. Must use '{authorized_sa_id}'. Execution blocked."
        }

    # 2. Robustness Check (MOCK for TDD)
    if space_name.startswith("spaces/FAIL_TRANSIENT"):
        # Simulates a transient error (e.g., 503 Service Unavailable) to test RetryConfig logic.
        return {
            "status": 503,
            "isError": True,
            "error_type": "SERVICE_UNAVAILABLE",
            "message": "Chat service is temporarily unavailable. The agent should apply exponential backoff and retry."
        }

    if space_name.startswith("spaces/FAIL_PERMANENT"):
        # Simulates a non-recoverable error (e.g., resource not found)
        return {
            "status": 404,
            "isError": True,
            "error_type": "SPACE_NOT_FOUND",
            "message": "The specified space was not found. Check the space_name and abort provisioning for this space."
        }

    # 3. Success (MOCK)
    return {
        "status": 200,
        "result": f"MOCK SUCCESS: Membership created for {employee_mail}.",
        "resource_name": f"{space_name}/members/{employee_mail}",
        "service_account_used": service_account_id
    }