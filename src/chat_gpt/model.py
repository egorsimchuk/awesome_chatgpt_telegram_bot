"""Chat gpt api processor"""
from typing import Dict, List

import openai
from loguru import logger


class Model:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self._conversation: List[Dict[str, str]] = [{"role": "system", "content": "You are a helpful assistant"}]

    def get_response(self, input_message: str):
        self._conversation.append({"role": "user", "content": input_message})
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self._conversation)["choices"][0]["message"][
            "content"
        ]
        self._conversation.append({"role": "assistant", "content": response})

        logger.info(f"Conversation history:\n{self._conversation}")

        return response
