import os
import time
import logging
import os
from dotenv import load_dotenv
from typing import Dict
from fastapi import FastAPI, HTTPException, Response, status
from app.schemas.question import Question
from app.services.factories import set_sql_agent, set_nlp_agent
from app.db.database import *
from app.db.database import create_engine_for_sql_database
from app.tasks.jobs import resetAgentsMemory, check_last_request_per_user, reset_llm
from app.tasks.scheduler import create_scheduler, add_memory_check_job, add_llm_reset_job, start_scheduler, stop_scheduler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
def initializeModel():
    app = FastAPI(
        title="API AZ Stock Management Chatbot",
        description="API for Stock Management Chatbot using SQL and NLP Agents",
        version="0.1",
    )

    async def startup_event():
        app.state.last_request_per_user = {}
        logging.info("Launch...")
        try :
            engine = create_engine_for_sql_database("mysql+pymysql:")
        except Exception as e:
            logging.error(f"Erreur connexion DB: {e}")

        app.state.sql_agent = set_sql_agent(engine)
        app.state.nlp_agent = set_nlp_agent()

        try:
            sched = create_scheduler()
            add_memory_check_job(sched, check_last_request_per_user, app, 1)
            add_llm_reset_job(sched, reset_llm, app)
            await start_scheduler(sched)
            app.state._scheduler = sched
        except Exception as e:
            logging.error(f"Failed to initialize scheduler: {e}")

    async def shutdown_event():
        try:
            sched = getattr(app.state, "_scheduler", None)
            if sched is not None:
                stop_scheduler(sched)
        except Exception as e:
            logging.error(f"Error stopping scheduler: {e}")
        try:
            resetAgentsMemory(app)
        except Exception as e:
            logging.error(f"Error resetting agents memory on shutdown: {e}")

        logging.info("Shutdown complete.")

    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)

    return app

app = initializeModel()


@app.post("/predict", status_code=200)
async def callBot(question: Question, response: Response):
    session_id = question.session_id
    user_question = question.question
    max_result_limit = 50
    
    app.state.last_request_per_user[session_id] = int(time.time())
    try:
        sql_result = app.state.sql_agent.get_response_with_memory(session_id, user_question)
        queries = clean_sql_query(sql_result.content, max_result_limit)
        data = execute_queries(app.state.sql_agent._engine, queries)
        
        logging.info(f"SQL Query: {queries}")
        if (isinstance(data, list)
            and len(data) == 1
            and isinstance(data[0], dict)
            and "rows_affected" in data[0]
            and data[0]["rows_affected"] == 0
        ): data = {"result": "no matching item"}
        final_response = app.state.nlp_agent.get_response_with_memory(
            session_id=session_id,
            user_question=user_question,
            dynamic_variables={
                "query": queries,
                "data": str(data),
                "result_limit": max_result_limit
            }
        )

        app.state.sql_agent._memory.rotate_history(session_id, 3)
        app.state.nlp_agent._memory.rotate_history(session_id, 3)
        logging.info(f"SQL Agent history : {app.state.sql_agent._memory.get_session_by_id(session_id)}")
        logging.info(f"NLP Agent history : {app.state.nlp_agent._memory.get_session_by_id(session_id)}")
        logging.info(f"Final response: {final_response.content}")

        return {
            "status": "success",
            "response": str(final_response.content)
        }

    except Exception as e:
        logging.error(f"Erreur lors du traitement: {e}")
        
        error_response = app.state.nlp_agent.get_response_with_memory(
            session_id=session_id,
            user_question=user_question,
            dynamic_variables={
                "query": queries if 'queries' in locals() else "Aucune requête générée",
                "data": str(e),
                "result_limit": max_result_limit
            }
        )

        response.status_code = 500
        return {
            "status": "error",
            "response": str(error_response.content)
        }