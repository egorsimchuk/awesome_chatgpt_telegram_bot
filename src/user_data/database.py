"""Database for storing users info"""
import pymongo
from loguru import logger
from pymongo.collection import Collection

from utils import utc_now


class Database:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://mongo:27017/")
        self.db = self.client["database"]
        self.users: Collection = self.db["users"]
        self.messages: Collection = self.db["messages"]

    def _create_user(self, user_id: int, username: str):
        self.users.insert_one({"_id": user_id, "username": username, "last_interaction_timestamp": utc_now()})

    def create_user_if_not_exist(self, user_id: int, username: str):
        if self.users.find_one({"_id": user_id}) is None:
            self._create_user(user_id, username)

    def _get_user_row(self, user_id: int):
        return self.users.find_one({"_id": user_id})

    def get_last_interaction_timestamp(self, user_id: int):
        return self._get_user_row(user_id)["last_interaction_timestamp"]

    def update_interaction_timestamp(self, user_id: int):
        self.users.update_one({"_id": user_id}, {"$set": {"last_interaction_timestamp": utc_now()}})

    def get_openai_api_key(self, user_id: int):
        user_row = self._get_user_row(user_id)
        logger.debug(f"user {user_id} get api_key {user_row.get('openai_api_key')}")
        if user_row:
            return user_row.get("openai_api_key")
        return None

    def set_openai_api_key(self, user_id: int, api_key: str):
        self.users.update_one({"_id": user_id}, {"$set": {"openai_api_key": api_key}})
        logger.debug(f"user {user_id} set api_key {api_key}")
