import os
from langchain_groq import ChatGroq
from app.services.chat import IAModel
from sqlalchemy.engine import Engine
from app.prompt.prompt import sql_prompt, nlp_prompt, init_prompt
from app.prompt.table_info import table_info

def set_sql_agent(engine: Engine) -> IAModel:
    sql_agent = IAModel()
    sql_agent.set_engine(engine)
    sql_agent.set_model(
            ChatGroq(api_key=os.getenv("GROQ_API_KEY"),
                     model_name=os.getenv("AI_MODEL"),
                     temperature=0.1,
                     max_retries=2))
    sql_agent.set_prompt(
            init_prompt([("system", sql_prompt)], table_info=table_info)
        )
    return sql_agent

def set_nlp_agent() -> IAModel:
    nlp_agent = IAModel()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("La clé API GROQ est manquante dans l'environnement")
    os.environ["GROQ_API_KEY"] = api_key
    nlp_agent.set_model(
        ChatGroq(api_key=os.getenv("GROQ_API_KEY"),
                 model_name=os.getenv("AI_MODEL"),
                 temperature=0.3, max_retries=2))
    nlp_agent.set_prompt(
        init_prompt(
                [("system", nlp_prompt)],)
                )
    return nlp_agent