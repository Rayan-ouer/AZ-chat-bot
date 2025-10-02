import os
import logging
from sqlalchemy import create_engine
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.memory import ConversationTokenBufferMemory
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate
from fastapi import FastAPI, HTTPException, Response, status
from app.model import IAModel
from app.prompt import *
from app.table_info import table_info

load_dotenv()

class Question(BaseModel):
    question: str
    session_id: int

origins = [
    "http://192.168.122.191:8000",
    "http://localhost:8000"
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    )

def create_db_and_tables(connection_string: str):
    engine = create_engine(
            connection_string
            + os.getenv(("AI_USERNAME"))
            + ":"
            + os.getenv(("AI_PASSWORD"))
            + "@"
            + os.getenv(("DB_HOST"))
            + ":"
            + os.getenv(("DB_PORT"))
            + "/"
            + os.getenv(("DB_DATABASE"))
        )
    return engine

def initializeModel():
    app = FastAPI(
        title="NegoBot Model API",
        description="Model NLP for Nego bot",
        version="0.1",
    )

    async def startup_event():
        logging.info("Launch...")
        engine = create_db_and_tables("mysql+pymysql://")
        app.state.llm = IAModel()
        app.state.llm.set_engine(engine)
        app.state.llm.set_model(
            ChatGroq(api_key=os.getenv("GROQ_API_KEY"),
                     model_name=os.getenv("AI_MODEL"),
                     temperature=0.1))

    async def shutdown_event():
        logging.info("Chutting down...")
        app.state.llm._memory.clear_all_sessions()

    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)

    return app

app = initializeModel()


@app.post("/predict", status_code=200)
async def callBot(question: Question, response: Response):
    app.state.llm._memory.create_session(question.session_id)
    app.state.llm._memory.add_user_message(question.session_id, question.question)
    app.state.llm._memory.reset_history(question.session_id, 3)

    sql_template = [
        ("system", sql_prompt),
        ("human", "{input}"),
    ]
    sql_variables = {
        "input": question.question,
        "table_info": table_info
    }
    sql_prompt_template = ChatPromptTemplate.from_messages(sql_template)
    app.state.llm.set_prompt(sql_prompt_template)
    data, request, is_executed = app.state.llm.runSQLRequest(sql_variables)
    if not is_executed:
        response.status_code = status.HTTP_201_CREATED
        app.state.llm._memory.add_ai_message(question.session_id, str(request))
        if "SELECT" in str(request):
            return {
                "status": "fail",
                "response": (
                    "❗ Je n’ai pas pu générer une recherche valide à partir de votre demande.\n\n"
                    "Cela peut venir d’un manque de précision ou d’un mot-clé absent.\n\n"
                    "🔍 Pour m’aider à mieux répondre, vous pouvez reformuler votre question en précisant :\n\n"
                    "    • Le type d’information que vous cherchez (ex : produits livrés, commandes en attente, chiffre d’affaires)\n"
                    "    • Une période ou un filtre éventuel (ex : ce mois-ci, pour un client précis)\n\n"
                    "💡 Exemples de questions efficaces :\n\n"
                    "    • “Quels sont les produits les plus rentables ce mois-ci ?”\n"
                    "    • “Combien de commandes ont été livrées pour le client Dupont ?”\n\n"
                    "Je suis là pour vous aider à transformer votre demande en recherche métier claire 😊"
                    )
                    }
        else: 
            return {
                "status": "fail",
                "response": str(request)
                }

    nlp_template = [
        ("system", nlp_prompt),
        ("human", "Question: {input}\nSQL Result: {resultats}\nSQL Query: {request}")
    ]
    nlp_variables = {
        "input": question.question,
        "request": request,
        "resultats": str(data)
    }
    nlp_prompt_template = ChatPromptTemplate.from_messages(nlp_template)
    app.state.llm.set_prompt(nlp_prompt_template)
    answer = app.state.llm.getResponseWithHistory(nlp_variables, question.session_id)
    return {
        "status": "success",
        "response": str(answer.content),
        "sql_query": request
    }