import pymongo as pymongo
from loguru import logger
from pymongo.collection import Collection

from utils import utc_now


class Database:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://mongo:mongo@localhost:27017/")
        self.db = self.client["database"]
        self.users: Collection = self.db["users"]
        self.messages: Collection = self.db["messages"]

    def _create_user(self, user_id: int, username: str):
        self.users.insert_one({"_id": user_id, "username": username, "last_interaction_timestamp": utc_now()})

    def create_user_if_not_exist(self, user_id: int, username: str):
        if self.users.find_one({"_id": user_id}) is None:
            self._create_user(user_id, username)

    def get_last_interaction_timestamp(self, user_id):
        row = self.users.find_one({"_id": user_id})
        if row:
            return row["last_interaction_timestamp"]
        else:
            logger.warning(f"Try fetch last_interaction_timestamp for not-existing user_id {user_id}")
