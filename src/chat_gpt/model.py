"""Chat gpt api processor"""
import json
from asyncio import sleep
from typing import Dict, List, Optional, Union

import openai
from loguru import logger
from openai import InvalidRequestError
from openai.error import RateLimitError
from pydantic import BaseModel

from utils import get_path_from_root_dir


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
    def __init__(
        self, processor_params: Optional[Dict] = None, model_params: Optional[Dict] = None, api_key: Optional[str] = None
    ):
        self.processor_params = ProcessorParams(**processor_params) if processor_params else ProcessorParams()
        self.model_params = ModelParams(**model_params) if model_params else ModelParams()
        self.set_openai_api_key(api_key)
        with open(get_path_from_root_dir("configs/chat_modes.json"), "rb") as f:
            self._chat_modes = json.load(f)
        self._conversation: List[Dict[str, str]] = None

    @property
    def conversation_initialized(self):
        return self._conversation is not None

    def set_openai_api_key(self, api_key: str):
        openai.api_key = api_key
        return self

    def switch_mode(self, promt: str):
        self._conversation: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": promt,
            }
        ]

    def get_response(
        self,
        input_message: str,
    ) -> Union[str, Exception]:
        self._conversation.append({"role": "user", "content": input_message})
        response = self._fetch_responce()
        if isinstance(response, str):
            self._conversation.append({"role": "assistant", "content": response})
        return response

    def _fetch_responce(self) -> str:
        error = None
        for i in range(self.processor_params.response_attempts):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", messages=self._conversation, **self.model_params.dict()
                )
                break
            except InvalidRequestError as err:
                error = err
                logger.error(f"Try {i}/{self.processor_params.response_attempts}. {err.error.message}")
                self._clip_conversation_history()
            except RateLimitError as err:
                error = err
                logger.error(f"Try {i}/{self.processor_params.response_attempts}. {err.error.message}")
                sleep(self.processor_params.wait_after_rate_limit_error)
            except Exception as err:
                error = err
                break
        try:
            return response["choices"][0]["message"]["content"]
        except NameError:
            return error

    def _clip_conversation_history(self, n: int = 1):
        for _ in range(n):
            if self._conversation:
                self._conversation.pop(0)
