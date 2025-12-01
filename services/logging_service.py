import logging
from typing import Optional, Any, Dict

# Basic Python logger configuration.
# This is typically overridden in a production environment to send logs to a managed service
# like Google Cloud Logging for persistence and analysis.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class LoggingService:
    """
    Service layer to handle all logging and exception reporting for the application.
    """
    def __init__(self, trace_id: Optional[str] = None):
        """
       Initializes the service. The 'trace_id' is critical for distributed tracing.
        """
        self.trace_id = trace_id
        self.logger = logging.getLogger('OnboardingAgent')

    def _format_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Formats the message for structured logging.
       In production, a structured JSON format is the gold standard.
        """
        log_data = {"message": message}
        if self.trace_id:
            #Injecting the Trace ID is crucial for Observability/Debugging
            log_data["trace_id"] = self.trace_id
        if context:
            #Merges specific operational context (e.g., project_id, role) into the log entry.
            log_data.update(context)

        # Simulates a concise structured output for the local terminal for readability.
        return f"[{self.trace_id or 'NO_TRACE'}] {message} - Context: {log_data}"

    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
       """Logs general information about the agent's actions (e.g., plan started)."""
       self.logger.info(self._format_message(message, context))

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
       Logs granular details for deep debugging (e.g., raw tool parameters or intermediate reasoning steps)[cite: 2762, 2761].
       Debug logs are highly detailed but can introduce performance overhead in production[cite: 2762].
        """
        self.logger.debug(self._format_message(message, context))

    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
       """Logs non-recoverable errors (e.g., API failure, critical logic issue)."""
       self.logger.error(self._format_message(message, context))

    def critical_exception(self, message: str, exception: Exception, context: Optional[Dict[str, Any]] = None):
        """
       Handles and logs critical exceptions, including traceback, and indicates a severe problem[cite: 2761].
       In real systems, this event should trigger an alert (Alerting) for the AgentOps team[cite: 2920].
        """
        self.logger.critical(self._format_message(message, context), exc_info=True)