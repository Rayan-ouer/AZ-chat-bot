import sqlparse
from sqlalchemy import text
from langchain_core.prompts import BasePromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from typing import Optional, Dict, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
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



class ChatMemory:
    def __init__(self):
        self._conversation: Dict[int, InMemoryChatMessageHistory] = {}
        self._counter_question: Dict[int, int] = {}

    def create_session(self, session_id: int):
        if session_id not in self._conversation:
            self._conversation[session_id] = InMemoryChatMessageHistory()
            self._counter_question[session_id] = 0
        return self._conversation[session_id]

    def get_session_by_id(self, session_id: int) -> InMemoryChatMessageHistory:
        if session_id not in self._conversation:
            return self.create_session(session_id)
        return self._conversation[session_id]

    def clear_history_by_id(self, session_id: int):
        if session_id in self._conversation:
            self._conversation[session_id] = InMemoryChatMessageHistory()
        if session_id in self._counter_question:
            self._counter_question[session_id] = 0
        
    def clear_all_sessions(self):
        for session_id in self._conversation:
            self._conversation[session_id].clear()
        self._conversation = {}
    
    def get_session_callable(self, session_id: int):
        def get_history(session_id: str) -> InMemoryChatMessageHistory:
            return self.create_session(session_id)
        return get_history
    
    def add_user_message(self, session_id: int, user_message):
        self._counter_question[session_id] += 1
        history = self.create_session(session_id)
        history.add_user_message(user_message)

    def add_ai_message(self, session_id: int, ai_message):
        history = self.create_session(session_id)
        history.add_ai_message(ai_message)

    def reset_history(self, session_id: int, max_question: int):
        counter = self._counter_question[session_id]
        if counter >= max_question:
            self.clear_history_by_id(session_id)

class IAModel:
    def __init__(self):
        self._model: Optional[BaseLanguageModel] = None
        self._prompt: Optional[BasePromptTemplate] = None
        self._engine = None
        self._memory = ChatMemory()

    def set_model(self, model: BaseLanguageModel):
        self._model = model
    
    def set_prompt(self, prompt: BasePromptTemplate):
        self._prompt = prompt

    def set_engine(self, engine):
        self._engine = engine

    def getResponse(self, variables: Dict[str, Any]):
        if not self._model or not self._prompt:
            raise RuntimeError("Le modèle et le prompt doivent être définis avant de générer une réponse.")
        
        chain = self._prompt | self._model
        return chain.invoke(variables)
    
    def getResponseWithHistory(self, variables: Dict[str, Any], session_id: int):
        if not self._model or not self._prompt:
            raise RuntimeError("Le modèle, le prompt et la mémoire doivent être définis.")
        
        try:
            print(f"Contenu de la mémoire: {self._memory.get_session_by_id(session_id)}")
        except Exception as e:
            print(f"Erreur lecture mémoire: {e}")
        
        chain = self._prompt | self._model
        #chain_with_history = RunnableWithMessageHistory(
        #    chain,
        #    self._memory.get_session_callable(session_id),
        #    input_messages_key="input",
        #    history_messages_key="history"
        #).with_config({"verbose": True})
    
        response = chain.invoke(
            variables,
            config={"configurable": {"session_id": session_id}}
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
        array_requests = cleaned_request.split(";")
        try:
            with self._engine.connect() as conn:
                for request in array_requests:
                    full_request = request + ";"
                    print("Request : ", full_request)
                    result = conn.execute(full_request)
                    data = result.fetchall()
                    data = [dict(row._mapping) for row in data]
                return data, cleaned_request, True
        except Exception as e:
            print(f"Erreur SQL : {e}")
            return data, cleaned_request, False

    