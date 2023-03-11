"""Chat gpt api processor"""
from asyncio import sleep
from typing import Dict, List, Optional

import openai
from loguru import logger
from openai import InvalidRequestError
from openai.error import RateLimitError
from pydantic import BaseModel


class ProcessorParams(BaseModel):
    response_attempts: int = 10
    wait_after_rate_limit_error: int = 60


class ModelParams(BaseModel):
    temperature: int = 0.7
    max_tokens: int = 1000
    top_p: int = 1
    frequency_penalty: int = 0
    presence_penalty: int = 0


class ChatGPT:
    def __init__(self, api_key: str, processor_params: Optional[Dict] = None, model_params: Optional[Dict] = None):
        openai.api_key = api_key
        self.processor_params = ProcessorParams(**processor_params) if processor_params else ProcessorParams()
        self.model_params = ModelParams(**model_params) if model_params else ModelParams()
        self._conversation: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": "As an advanced chatbot named ChatGPT, your primary goal is to assist users to the best of your ability. This may involve answering questions, providing helpful information, or completing tasks based on user input. In order to effectively assist users, it is important to be detailed and thorough in your responses. Use examples and evidence to support your points and justify your recommendations or solutions. Remember to always prioritize the needs and satisfaction of the user. Your ultimate goal is to provide a helpful and enjoyable experience for the user.",
            }
        ]

    def get_response(self, input_message: str):
        self._conversation.append({"role": "user", "content": input_message})
        response = self._fetch_responce()
        self._conversation.append({"role": "assistant", "content": response})
        return response

    def _fetch_responce(self):
        err_message = None
        for i in range(self.processor_params.response_attempts):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", messages=self._conversation, **self.model_params.dict()
                )
                break
            except InvalidRequestError as err:
                err_message = err.error.message
                logger.error(f"Try {i}/{self.processor_params.response_attempts}. {err_message}")
                self._clip_conversation_history()
            except RateLimitError as err:
                err_message = err.error.message
                logger.error(f"Try {i}/{self.processor_params.response_attempts}. {err_message}")
                sleep(self.processor_params.wait_after_rate_limit_error)
        try:
            return response["choices"][0]["message"]["content"]
        except NameError:
            return err_message

    def _clip_conversation_history(self, n: int = 1):
        for _ in range(n):
            if self._conversation:
                self._conversation.pop(0)
