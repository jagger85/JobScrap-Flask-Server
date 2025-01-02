from .BaseModel import BaseModel
from datetime import datetime
from bson import ObjectId

class AutomatedScrapOperationModel(BaseModel):
    def __init__(self, db):
        super().__init__(db, "AutomatedScrapOperations")

    def create_automated_scrap_operation(self, data):
        data["created_at"] = datetime.utcnow()
        return self.create(data)

    def get_automated_scrap_operation_by_id(self, id):
        return self.collection.find_one({"_id": ObjectId(id)})

    def get_all_automated_scrap_operations(self):
        return list(self.collection.find({}, {"_id": 0}))

    def delete_automated_scrap_operation(self, id):
        return self.collection.delete_one({"_id": ObjectId(id)})

    def activate_automated_scrap_operation(self, id):
        return self.collection.update_one({"_id": ObjectId(id)}, {"$set": {"active": True}})

    def deactivate_automated_scrap_operation(self, id):
        return self.collection.update_one({"_id": ObjectId(id)}, {"$set": {"active": False}})

    def increment_automated_scrap_operation_count(self, id):
        return self.collection.update_one({"_id": ObjectId(id)}, {"$inc": {"count": 1}})

    def update_last_scraped_at(self, id):
        return self.collection.update_one({"_id": ObjectId(id)}, {"$set": {"last_scraped_at": datetime.utcnow()}})
