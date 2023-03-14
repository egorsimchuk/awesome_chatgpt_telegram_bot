"""Container for users models"""
from typing import Dict

from chat_gpt.model import ChatGPT


class UserModels:
    def __init__(self):
        self._models: Dict[int:ChatGPT] = {}

    def get_model(self, chat_id: int, api_key: str) -> ChatGPT:
        if chat_id not in self._models:
            self._models[chat_id] = ChatGPT(api_key=api_key)
        return self._models[chat_id].set_openai_api_key(api_key)
