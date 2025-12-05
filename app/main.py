import time
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from starlette.concurrency import run_in_threadpool
from app.schemas.question import Question
from app.services.factories import set_sql_agent, set_nlp_agent
from app.db.database import (
    create_engine_for_sql_database,
    verify_and_extract_sql_query,
    execute_queries,
    is_empty_result,
)
from app.tasks.jobs import reset_agents_memory, check_last_request_per_user, reset_llm
from app.tasks.scheduler import (
    create_scheduler,
    add_memory_check_job,
    add_llm_reset_job,
    start_scheduler,
    stop_scheduler,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
def initialize_app():
    app = FastAPI(
        title="API AZ Stock Management Chatbot",
        description="API for Stock Management Chatbot using SQL and NLP Agents",
        version="0.1",
    )

    async def startup_event():
        app.state.last_request_per_user = {}
        logging.info("Application startup initiated...")
        try:
            engine = create_engine_for_sql_database("mysql+pymysql:")
        except Exception as e:
            logging.exception("Database engine initialization failed: %s", e)
            raise RuntimeError("Cannot initialize database engine") from e

        app.state.sql_agent = set_sql_agent(engine)
        app.state.nlp_agent = set_nlp_agent()

        try:
            sched = create_scheduler()
            add_memory_check_job(sched, check_last_request_per_user, app, 1)
            add_llm_reset_job(sched, reset_llm, app)
            await start_scheduler(sched)
            app.state._scheduler = sched
            logging.info("Scheduler initialized successfully")
        except Exception as e:
            logging.exception("Failed to initialize scheduler: %s", e)
            raise RuntimeError("Scheduler initialization failed") from e

    async def shutdown_event():
        try:
            sched = getattr(app.state, "_scheduler", None)
            if sched is not None:
                stop_scheduler(sched)
        except Exception as e:
            logging.error("Error stopping scheduler: %s", e)
        try:
            reset_agents_memory(app)
        except Exception as e:
            logging.error("Error resetting agents memory on shutdown: %s", e)

        logging.info("Shutdown complete.")

    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)

    return app

app = initialize_app()

@app.post("/predict")
async def get_ai_response(question: Question, response: Response):
    session_id = question.session_id
    user_question = question.question
    max_result_limit = 50
    
    app.state.last_request_per_user[session_id] = int(time.time())
    try:
        sql_result = await run_in_threadpool(
            lambda: app.state.sql_agent.get_response_with_memory(session_id, user_question)
        )
        queries = verify_and_extract_sql_query(sql_result.content, max_result_limit)
        data = await run_in_threadpool(
            lambda: execute_queries(app.state.sql_agent.get_engine(), queries)
        )
        if is_empty_result(data):
            data = {"result": "no matching item"}

        final_response = await run_in_threadpool(
            lambda: app.state.nlp_agent.get_response_with_memory(
                session_id=session_id,
                user_question=user_question,
                dynamic_variables={
                    "query": queries,
                    "data": str(data),
                    "result_limit": max_result_limit,
                },
            )
        )
        app.state.sql_agent.get_memory().rotate_history(session_id, max_questions=3)
        app.state.nlp_agent.get_memory().rotate_history(session_id, max_questions=3)
        return {
            "status": "success",
            "response": str(final_response.content),
        }

    except Exception as e:
        logging.exception("Error processing request for session %s: %s", session_id, e)
        try:
            error_response = await run_in_threadpool(
                lambda: app.state.nlp_agent.get_response_with_memory(
                    session_id=session_id,
                    user_question=user_question,
                    dynamic_variables={
                        "query": queries if 'queries' in locals() else ["No query generated"],
                        "data": str(e),
                        "result_limit": max_result_limit,
                    },
                )
            )
            response.status_code = 200
            return {
                "status": "success",
                "response": str(error_response.content),
            }
        except Exception as nlp_error:
            logging.exception("NLP agent error after SQL failure: %s", nlp_error)
            response.status_code = 500
            return {
                "status": "error",
                "response": "Internal server error. Please retry later.",
            }