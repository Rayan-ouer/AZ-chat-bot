import os
import sqlparse
from sqlalchemy import create_engine
from table_info import table_info
from sqlalchemy import text
from langchain_groq import ChatGroq
from langchain_core.prompts import BasePromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from typing import Optional, Dict, Any, Tuple, List
from langchain_core.language_models import BaseLanguageModel
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage

def getBodyStr(sentence: str, start: str, end: str):
    sentence_list = sentence.split()
    res = []
    switch: bool = False

    for indexed_sentence in sentence_list:
        if indexed_sentence == start:
            switch = True
        if switch == True:
            res.append(indexed_sentence)
        if indexed_sentence.find(end) != -1:
            switch = False
    return " ".join(res)


def sqlRequestMiddleware(responsesql: str):
    parsed_sql = sqlparse.format(responsesql, reindent=True, keyword_case="upper")
    replaced_sql = getBodyStr(parsed_sql, "SELECT", ";")
    if not replaced_sql:
        return None
    return replaced_sql


class IAModel:
    def __init__(self):
        self._model: Optional[BaseLanguageModel] = None
        self._prompt: Optional[BasePromptTemplate] = None
        self._engine = None
        self._memory: Optional[BaseChatMessageHistory]

    def set_model(self, model: BaseLanguageModel):
        self._model = model
    
    def set_prompt(self, prompt: BasePromptTemplate):
        self._prompt = prompt

    def set_engine(self, engine):
        self._engine = engine

    def set_memory(self, memory: BaseChatMessageHistory):
        self._memory = memory

    def getResponse(self, variables: Dict[str, Any]):
        if not self._model or not self._prompt:
            raise RuntimeError("Le modèle et le prompt doivent être définis avant de générer une réponse.")
        
        chain = self._prompt | self._model
        return chain.invoke(variables)
    
    def getResponseWithHistory(self, variables: Dict[str, Any]):
        if not self._model or not self._prompt:
            raise RuntimeError("Le modèle, le prompt et la mémoire doivent être définis.")
        
        # Debug: voir le contenu de la mémoire
        #try:
        #    print(f"Contenu de la mémoire: {self._memory}")
        #except Exception as e:
        #    print(f"Erreur lecture mémoire: {e}")
        
        chain = self._prompt | self._model
        # Configuration de la chaîne avec historique
       ## chain_with_history = RunnableWithMessageHistory(
       ##     chain,
       ##     input_messages_key="input",
       ##     history_messages_key="history"
       ## )
        
        # Exécution
        response = chain.invoke(
            variables,
            config={"configurable": {"session_id": "default"}}
        )
        
        return response

    def cleanSQLRequest(self, request) -> Optional[str]:
        return sqlRequestMiddleware(request)

    def runSQLRequest(self, variables: Dict[str, Any]):
        if not self._engine:
            raise RuntimeError("Le moteur SQL doit être défini avant d'exécuter la requête.")

        data = []
        raw_response = self.getResponse(variables)
        
        if isinstance(raw_response, AIMessage):
            raw_request = raw_response.content
        else:
            raw_request = str(raw_response)
            
        cleaned_request = self.cleanSQLRequest(raw_request)
        
        if not cleaned_request:
            return data, raw_request, False

        try:
            with self._engine.connect() as conn:
                result = conn.execute(text(cleaned_request))
                data = result.fetchall()
                data = [dict(row._mapping) for row in data]
            return data, cleaned_request, True
        except Exception as e:
            print(f"Erreur SQL : {e}")
            return data, cleaned_request, False