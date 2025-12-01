import logging
import json
from typing import Dict, Any, Optional, List
from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy import text, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from config.settings import Config
from typing import Any

logger = logging.getLogger("OnboardingProtocolService")


# ----------------------------------------------------------------------
# 0. MODEL DEFINITION (SQLAlchemy Schema)
# ----------------------------------------------------------------------

class Base(DeclarativeBase):
    """Base class for database tables (SQLAlchemy ORM base)."""
    pass

class Protocol(Base):
    """Represents a static Onboarding Protocol artifact stored in the RAG DB."""
    __tablename__ = "protocols"

    # Columns mapped with SQLAlchemy types for table creation
    project_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    principal_email: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(String(20))
    # Stores the steps list as TEXT (simulates JSONB)
    required_steps: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)


# ----------------------------------------------------------------------
# 1. HELPER FUNCTION: DB Row Parsing (SRP: Business Domain Mapping)
# ----------------------------------------------------------------------

def _map_db_row_to_protocol_dict(row: Any) -> Dict[str, Any]:
    """
    Helper function to map a single SQLAlchemy row object into the standardized
    Protocol dictionary format expected by the LLM Agent.

    This ensures the Agent's Tool always receives predictable, canonical JSON.
    """
    if not row:
        return {"protocol_found": False, "status": 404, "message": "Protocol not found in live DB."}

    # Maps DB columns to the required Agent context format.
    return {
        "protocol_found": True,
        "required_steps": row.required_steps,
        "protocol_version": row.version,
        "status": 200,
        "message": "LIVE: Protocol retrieved successfully."
    }


# ----------------------------------------------------------------------
# 2. PROTOCOL SERVICE CLASS (SRP: Infrastructure and Connection)
# ----------------------------------------------------------------------

class RagProtocolDBServiceImpl:
    """
    Handles the connection and logic for the static, Application-Level Protocol Database (RAG Source).

    Manages the connection, health check, schema creation, and data persistence.
    """

    def __init__(self, protocol_db_url: str):
        self.db_url = protocol_db_url
        self.engine: Optional[Engine] = None
        self.is_connected: bool = False

        # Connection logic is attempted only if not in deterministic test mode
        if Config.ENV_PROFILE != "test":
            try:
                # 1. Create DB engine and attempt connection
                self.engine = create_engine(protocol_db_url)

                # 2. Connection Verification (Health Check: SELECT 1)
                with self.engine.connect() as connection:
                    connection.execute(text("SELECT 1"))

                self.is_connected = True
                logger.info("ProtocolDBService connected successfully to PostgreSQL.")

                # 3. Initialize Schema and Seed Data (Flyway/Alembic equivalent)
                self._initialize_schema_and_data()

            except OperationalError as e:
                logger.error(f"FATAL DB ERROR: Could not connect to Protocol DB at {protocol_db_url}. Ensure container is running.")
            except Exception as e:
                logger.error(f"Unexpected error during DB connection: {e}")


    def _initialize_schema_and_data(self):
        """
        Creates the 'protocols' table schema and inserts initial seed data (PROJ-ALPHA).
        This ensures the RAG source is primed for the Coordinator Agent's lookup.
        """
        logger.info("Initializing Protocol Database schema and seeding initial data...")

        # 1. SCHEMA CREATION: Creates all tables defined under Base (the 'protocols' table)
        if self.engine:
            Base.metadata.create_all(self.engine)

        # 2. Seeding Initial Data (PROJ-ALPHA)
        initial_protocol_id = "PROJ-ALPHA"

        with self.engine.connect() as conn:
            # Check if data already exists to prevent duplication
            check_query = text("SELECT 1 FROM protocols WHERE project_id = :id")
            if conn.execute(check_query, {"id": initial_protocol_id}).fetchone() is None:

                # Canonical steps structure (stored as JSON string/Text)
                steps_json = json.dumps({
                    "enterprise": ["Gchat Provisioning", "Drive Access Setup"],
                    "client": ["Client Azure Account Request", "Client Repo Access"]
                })

                insert_query = text("""
                                    INSERT INTO protocols (project_id, principal_email, version, required_steps, is_active)
                                    VALUES (:id, :principal, :version, :steps_json, TRUE)
                                    """)

                conn.execute(
                    insert_query,
                    {
                        "id": initial_protocol_id,
                        "principal": "system_admin@enterprise.com",
                        "version": "v2.1",
                        "steps_json": steps_json
                    }
                )
                conn.commit()
                logger.info(f"Protocol {initial_protocol_id} seeded successfully.")


    # ----------------------------------------------------------------------
    # 3. PUBLIC METHODS (Used by RAGProtocolService Abstraction Layer)
    # ----------------------------------------------------------------------

    def get_protocol(self, project_id: str) -> Dict[str, Any]:
        """
        Retrieves the protocol status, using MOCK data for 'test' or attempting
        a real database query otherwise.
        """

        # 1. TOGGLE: MOCK LOGIC FOR TDD
        if Config.is_test_mode():
            logger.info("Using MOCK protocol data for unit testing.")
            # Deterministic MOCK logic (as previously defined)
            if project_id == "PROJ-ALPHA":
                return {"protocol_found": True, "required_steps": ["Gchat"], "status": 200, "message": "MOCK: Protocol found."}
            if project_id == "PROJ-BETA":
                return {"protocol_found": False, "status": 404, "is_user_authorized_to_create": True, "message": "MOCK: Protocol not found, authorized to create."}
            return {"protocol_found": False, "status": 404, "message": "MOCK: Project ID not recognized."}


        # 2. LIVE EXECUTION LOGIC (dev/prod)

        if not self.is_connected or self.engine is None:
            return {"protocol_found": False, "status": 503, "isError": True, "message": "Protocol DB is offline. Cannot perform RAG lookup."}

        # --- REAL DB QUERY IMPLEMENTATION ---
        try:
            with self.engine.connect() as connection:
                # Parameterized query to fetch active protocol data
                query = text("SELECT required_steps, version, project_id FROM protocols WHERE project_id = :id AND is_active = TRUE")
                result = connection.execute(query, {"id": project_id})
                row = result.fetchone()

            # Use the helper function to format the result into the canonical dictionary
            return _map_db_row_to_protocol_dict(row)

        except Exception as e:
            logger.error(f"Error during live protocol retrieval for {project_id}: {e}")
            return {"protocol_found": False, "status": 500, "isError": True, "message": "LIVE: Failed to execute database query."}


    def create_protocol(self, project_id: str, principal_email: str) -> Dict[str, Any]:
        """
        Simulates the creation and persistence (write operation) of a new, draft protocol artifact in the database.
        """
        if Config.is_test_mode():
            return {"status": 201, "protocol_version": "v1.0 (Mock Draft)", "message": "New protocol draft successfully created (MOCK)."}

        if not self.is_connected or self.engine is None:
            return {"status": 503, "isError": True, "message": "Protocol DB is offline. Cannot create artifact."}

        # --- REAL DB WRITE IMPLEMENTATION ---
        try:
            with self.engine.connect() as conn:
                # Creates a basic draft protocol entry with minimal steps
                insert_query = text("INSERT INTO protocols (project_id, principal_email, version, required_steps, is_active) VALUES (:id, :principal, 'v1.0 (Draft)', '[]', TRUE)")
                conn.execute(insert_query, {"id": project_id, "principal": principal_email})
                conn.commit()

            logger.info(f"Protocol artifact created in DB for {project_id} by {principal_email}.")

            return {
                "status": 201,
                "protocol_version": "v1.0 (Draft)",
                "message": "New protocol draft successfully created in the persistent store."
            }
        except Exception as e:
            logger.error(f"Error during live protocol creation for {project_id}: {e}")
            return {"status": 500, "isError": True, "message": "LIVE: Failed to execute database write operation."}