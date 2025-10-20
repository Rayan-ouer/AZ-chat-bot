import time
import os
import logging
from typing import Optional

def resetAgentsMemory(app) -> None:
    try:
        if hasattr(app.state, "sql_agent"):
            app.state.sql_agent._memory.clear_all_sessions()
        if hasattr(app.state, "nlp_agent"):
            app.state.nlp_agent._memory.clear_all_sessions()
        logging.info("Agents memory reset successfully.")
    except Exception as e:
        logging.error(f"Error resetting agents memory: {e}")


def reset_memory_user(app, session_id: int) -> None:
    logging.info(f"Resetting memory for user: {session_id}...")
    try:
        if hasattr(app.state, "sql_agent"):
            app.state.sql_agent._memory.clear_history_by_id(session_id)
        if hasattr(app.state, "nlp_agent"):
            app.state.nlp_agent._memory.clear_history_by_id(session_id)
        logging.info(f"Memory for session_id: {session_id} reset successfully.")
    except Exception as e:
        logging.error(f"Error resetting memory for session_id {session_id}: {e}")


def check_last_request_per_user(app, timeout_seconds: Optional[int] = None) -> None:
    try:
        current_time = int(time.time())
        default_timeout = int(os.getenv("MEMORY_TIMEOUT_SECONDS", str(10 * 60)))
        timeout_threshold = timeout_seconds if timeout_seconds is not None else default_timeout

        last_map = getattr(app.state, "last_request_per_user", {})
        for session_id, last_request_time in list(last_map.items()):
            if current_time - last_request_time > timeout_threshold:
                reset_memory_user(app, session_id)
                try:
                    del app.state.last_request_per_user[session_id]
                except Exception:
                    pass
                logging.info(
                    f"Session {session_id} has been inactive for over {timeout_threshold} seconds. Memory reset."
                )
    except Exception as e:
        logging.error(f"Error checking last request per user: {e}")