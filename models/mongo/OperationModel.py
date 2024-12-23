from .BaseModel import BaseModel
from .validate_data import validate_data
from datetime import datetime
from bson import ObjectId
class OperationModel(BaseModel):

    REQUIRED_FIELDS = ["platform", "user", "time_range", "keywords"]

    def __init__(self, db):
        super().__init__(db,"Operations")

    def create_operation(self, data):
        if validate_data(data, self.REQUIRED_FIELDS):
            data["created_at"] = datetime.utcnow()
            return self.create(data)
    
    def get_all_operations(self):
        return list(self.collection.find({}, {"_id":0}))
        
    def set_listings(self, document_id, listings):
        self.collection.update_one({"_id": ObjectId(document_id)}, {"$set": {"listings": listings}})
    
    def set_result(self, document_id, result):
        self.collection.update_one({"_id": ObjectId(document_id)}, {"$set": {"success": result}})
