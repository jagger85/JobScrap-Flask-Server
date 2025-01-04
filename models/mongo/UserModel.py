from .BaseModel import BaseModel
from datetime import datetime
from bson import ObjectId
class UserModel(BaseModel):

    REQUIRED_FIELDS = ["username", "password", "role"]

    def __init__(self, db):
        super().__init__(db, "Users")


    def find_by_username(self, username):
        return self.collection.find_one({"username": username})

    def create_user(self, data):
        if self.validate_data(data, self.REQUIRED_FIELDS):
            data["created_at"] = datetime.utcnow(),
            return self.create(data)

    def delete_user(self, username):
        return self.collection.delete_one({"username": username})

    def get_all_users(self):
        return list(self.collection.find({}, {"_id": 0, "password": 0}))

    def get_user_with_id(self, id):
        return self.collection.find_one({"_id": ObjectId(id)}, {"_id": 0, "password": 0})

    def get_id_with_username(self, username):
        return str(self.collection.find_one({"username": username}, {"_id": 1})["_id"]) if self.collection.find_one({"username": username}) else None

    def get_role_with_username(self, username):
        user = self.collection.find_one({"username": username}, {"_id": 0, "role": 1})
        return user["role"] if user else None

    def update_password(self, username, new_password):
        try:
            result = self.collection.update_one(
                {"username": username},
                {"$set": {"password": new_password}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating password: {e}")
            return False
