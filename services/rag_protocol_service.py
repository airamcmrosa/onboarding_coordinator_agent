from typing import Dict, Any
from services.rag_protocol_impl import RagProtocolDBServiceImpl

class RAGProtocolService:
    """
    Abstractions the data access layer for the Onboarding Protocol (RAG Source).

    This service translates business requests (e.g., check status) into database
    operations, separating business logic from SQL implementation details.
    """

    def __init__(self, db_service: RagProtocolDBServiceImpl):
        self.db_service = db_service

    def get_protocol_status(self, project_id: str) -> Dict[str, Any]:
        """Checks if a protocol exists and retrieves its content (RAG Lookup)."""
        return self.db_service.get_protocol(project_id)

    def create_new_protocol_draft(self, project_id: str, principal_email: str) -> Dict[str, Any]:
        """Creates a new protocol artifact in the persistent store."""
        return self.db_service.create_protocol(project_id, principal_email)
