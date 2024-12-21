from .BaseModel import BaseModel
from .validate_data import validate_data

class UserModel(BaseModel):

    REQUIRED_FIELDS = ["username", "password", "role"]

    def __init__(self, db):
        super().__init__(db, "Users")


    def find_by_username(self, username):
        return self.collection.find_one({"username": username})

    def create_user(self, data):
        if validate_data(data, self.REQUIRED_FIELDS):
            return self.create(data)

    def delete_user(self, username):
        return self.collection.delete_one({"username": username})

    def get_all_users(self):
        return list(self.collection.find({}, {"_id": 0, "password": 0}))