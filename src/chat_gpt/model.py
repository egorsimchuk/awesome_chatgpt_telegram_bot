"""Chat gpt api processor"""
from asyncio import sleep
from typing import Dict, List

import openai
from loguru import logger
from openai import InvalidRequestError
from openai.error import RateLimitError

ATTEMPS = 10


class Model:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self._conversation: List[Dict[str, str]] = [{"role": "system", "content": "You are a helpful assistant"}]

    async def get_response(self, input_message: str):
        self._conversation.append({"role": "user", "content": input_message})
        response = await self._fetch_responce()
        self._conversation.append({"role": "assistant", "content": response})
        return response

    async def _fetch_responce(self):
        err_message = None
        for i in range(ATTEMPS):
            try:
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self._conversation)
            except InvalidRequestError as err:
                err_message = err.error.message
                logger.error(f"Try {i}/{ATTEMPS}. {err_message}")
                self._clip_conversation_history()
            except RateLimitError as err:
                err_message = err.error.message
                logger.error(f"Try {i}/{ATTEMPS}. {err_message}")
                await sleep(60)
        try:
            return response["choices"][0]["message"]["content"]
        except NameError:
            return err_message

    def _clip_conversation_history(self, n: int = 2):
        for _ in range(n):
            if self._conversation:
                self._conversation.pop(0)
