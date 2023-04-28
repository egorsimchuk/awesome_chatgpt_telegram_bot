"""Database for storing users info"""
from typing import Dict

from loguru import logger

from utils import utc_now


class Database:
    def __init__(self):
        self.users: Dict[str] = {}

    def _create_user(self, user_id: int, username: str):
        self.users[user_id] = {"username": username, "last_interaction_timestamp": utc_now()}

    def create_user_if_not_exist(self, user_id: int, username: str):
        if user_id not in self.users:
            self._create_user(user_id, username)

    def _get_user_row(self, user_id: int):
        return self.users.get(user_id)

    def get_last_interaction_timestamp(self, user_id: int):
        return self._get_user_row(user_id)["last_interaction_timestamp"]

    def update_interaction_timestamp(self, user_id: int):
        self.users[user_id]["last_interaction_timestamp"] = utc_now()

    def get_openai_api_key(self, user_id: int):
        user_row = self._get_user_row(user_id)
        logger.debug(f"user {user_id} get api_key {user_row.get('openai_api_key')}")
        if user_row:
            return user_row.get("openai_api_key")
        return None

    def set_openai_api_key(self, user_id: int, api_key: str):
        self.users[user_id]["openai_api_key"] = api_key
        logger.debug(f"user {user_id} set api_key {api_key}")
