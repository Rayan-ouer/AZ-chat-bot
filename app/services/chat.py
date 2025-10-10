from langchain_core.prompts import BasePromptTemplate
from typing import Optional, Dict, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage

class ChatMemory:
    def __init__(self):
        self._conversation: Dict[int, InMemoryChatMessageHistory] = {}
        self._counter_question: Dict[int, int] = {}
        
    def get_session_by_id(self, session_id: int) -> InMemoryChatMessageHistory:
        if session_id not in self._conversation:
            self._conversation[session_id] = InMemoryChatMessageHistory()
            self._counter_question[session_id] = 0
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
            return self.get_session_by_id(session_id)
        return get_history
    
    def add_user_message(self, session_id: int, user_message):
        history = self.get_session_by_id(session_id)
        self._counter_question[session_id] += 1
        history.add_user_message(user_message)

    def add_ai_message(self, session_id: int, ai_message):
        history = self.get_session_by_id(session_id)
        history.add_ai_message(ai_message)

    def reset_history(self, session_id: int, max_question: int):
        if session_id not in self._counter_question:
            return
        counter = self._counter_question[session_id]
        if counter >= max_question:
            self.clear_history_by_id(session_id)
    
    def rotate_history(self, session_id: int, max_questions: int):
        if session_id not in self._conversation:
            return
        history = self._conversation[session_id]
        total_messages = len(history.messages)
        max_messages = max_questions * 2
        if total_messages > max_messages:
            messages_to_keep = history.messages[-max_messages:]
            history.messages = messages_to_keep
            self._counter_question[session_id] = max_questions

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
    
    def get_response(self, variables: Dict[str, Any]):
        if not self._model or not self._prompt:
            raise RuntimeError("The template and prompt must be defined before generating a response.")

        chain = self._prompt | self._model
        return chain.invoke(variables)
    
    def get_response_with_memory(self, session_id: int, user_question: Optional[str] = None, add_to_history: bool = True,
                                 dynamic_variables: Optional[Dict[str, Any]] = None, **invoke_kwargs
        ) -> AIMessage:
        if user_question is not None and add_to_history:
            self._memory.add_user_message(session_id, user_question)

        history = self._memory.get_session_by_id(session_id)
        prompt_copy = self._prompt.model_copy()
        print(f"History : {history}")
        for message in history.messages:
            prompt_copy.messages.append(message)

        chain = prompt_copy | self._model
        result = chain.invoke(dynamic_variables or {}, **invoke_kwargs)

        if add_to_history:
            self._memory.add_ai_message(session_id, result.content)

        return result