import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.memory import ConversationTokenBufferMemory
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate
from fastapi import FastAPI, HTTPException, Response, status
from langchain_core.chat_history import InMemoryChatMessageHistory
from model import IAModel
from prompt import *
from table_info import table_info

load_dotenv()

chats_by_session_id = {}

class Question(BaseModel):
    question: str

origins = [
    "http://192.168.122.191:8000",
    "http://localhost:8000"
]

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

def get_chat_history(session_id: str) -> InMemoryChatMessageHistory:
    chat_history = chats_by_session_id.get(session_id)
    if chat_history is None:
        chat_history = InMemoryChatMessageHistory()
        chats_by_session_id[session_id] = chat_history
    return chat_history

def initializeModel():
    app = FastAPI(
        title="NegoBot Model API",
        description="Model NLP for Nego bot",
        version="0.1",
    )
    session_id = "default"
    async def startup_event():
        print("Launch...")
        engine = create_db_and_tables("mysql+pymysql://")
        app.state.llm = IAModel()
        app.state.llm.set_engine(engine)
        app.state.llm.set_model(
            ChatGroq(api_key=os.getenv("GROQ_API_KEY"),
                     model_name=os.getenv("AI_MODEL"),
                     temperature=0.1))

    async def shutdown_event():
        print("Shut down")

    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)

    return app

app = initializeModel()


@app.post("/predict", status_code=200)
async def callBot(question: Question, response: Response):
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
    print(f"CONTENU : {request}")
    
    if not is_executed:
        response.status_code = status.HTTP_201_CREATED
        return {
            "status": "fail",
            "response": str(request)
        }

    # NLP Response Generation Phase
    nlp_template = [
        ("system", nlp_prompt),
        ("human", "Question: {input}\nSQL Result: {resultats}\nSQL Query: {request}")
    ]
    
    nlp_variables = {
        "input": question.question,
        "request": request,
        "resultats": str(data)  # Convert data to string for the prompt
    }
    
    nlp_prompt_template = ChatPromptTemplate.from_messages(nlp_template)
    app.state.llm.set_prompt(nlp_prompt_template)
    
    # Use history if available, otherwise get basic response
   # if app.state.llm._memory:
    answer = app.state.llm.getResponseWithHistory(nlp_variables)
    #else:
    #    answer = app.state.llm.getResponse(nlp_variables)
    
    return {
        "status": "success",
        "response": str(answer.content),
        "sql_query": request  # Optional: return SQL for debugging
    }