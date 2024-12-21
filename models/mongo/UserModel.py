from .BaseModel import BaseModel

class UserModel(BaseModel):

    REQUIRED_FIELDS = ["username", "password", "role"]

    def __init__(self, db):
        super().__init__(db, "Users")

    def _validate_data(self, data):
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

    def find_by_username(self, username):
        return self.collection.find_one({"username": username})

    def create_user(self, data):
        self._validate_data(data)
        return self.create(data)

    def delete_user(self, username):
        return self.collection.delete_one({"username": username})

    def get_all_users(self):
        return list(self.collection.find({}, {"_id": 0, "password": 0}))