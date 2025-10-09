import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response, status
from app.schemas.question import Question
from app.services.factories import set_sql_agent, set_nlp_agent
from app.db.database import *
from app.db.database import create_engine_for_sql_database

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def initializeModel():
    app = FastAPI(
        title="NegoBot Model API",
        description="Model NLP for Nego bot",
        version="0.1",
    )

    async def startup_event():
        logging.info("Launch...")
        try :
            engine = create_engine_for_sql_database("mysql+pymysql:")
        except Exception as e:
            logging.error(f"Erreur connexion DB: {e}")

        app.state.sql_agent = set_sql_agent(engine)
        app.state.nlp_agent = set_nlp_agent(engine)

    async def shutdown_event():
        logging.info("Chutting down...")
        app.state.sql_agent._memory.clear_all_sessions()
        app.state.nlp_agent._memory.clear_all_sessions()

    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)

    return app

app = initializeModel()

@app.post("/predict", status_code=200)
async def callBot(question: Question, response: Response):
    session_id = question.session_id
    result = app.state.sql_agent.get_response_with_memory(session_id, question.question, True)
    queries = clean_sql_query(result.content)
    data = execute_queries(app.state.sql_agent._engine, queries)

    logging.info(f"SQL Query: {queries}")
    logging.info(f"Data: {str(data)}")
    logging.info(f"History: {app.state.nlp_agent._memory.get_session_by_id(session_id)}")

    app.state.nlp_agent._memory = app.state.sql_agent._memory
    final_response = app.state.nlp_agent.get_response_with_memory(session_id, user_question=None,
        add_to_history=False,
        dynamic_variables={"data": str(data)})
    app.state.sql_agent._memory.reset_history(session_id, 3)
    return {
        "status": "success",
        "response": str(final_response.content)
    }