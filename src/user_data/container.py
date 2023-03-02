"""Container for users models"""
from typing import Dict

from src.chat_gpt.model import Model


class UserModels:
    def __init__(self):
        self._models: Dict[int:Model] = {}

    def get_model(self, chat_id: int, api_key: str):
        if chat_id not in self._models:
            self._models[chat_id] = Model(api_key)
        return self._models[chat_id]
