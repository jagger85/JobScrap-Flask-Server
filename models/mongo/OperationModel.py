from .BaseModel import BaseModel
from datetime import datetime
from bson import ObjectId
class OperationModel(BaseModel):

    REQUIRED_FIELDS = ["platform", "user", "time_range", "keywords"]

    def __init__(self, db):
        super().__init__(db,"Operations")

    def create_operation(self, data):
        if self.validate_data(data, self.REQUIRED_FIELDS):
            data["created_at"] = datetime.utcnow()
            return self.create(data)
    
    def get_all_operations(self):
        operations = list(self.collection.find({}))
        # Convert ObjectId to string for each document
        for op in operations:
            op['_id'] = str(op['_id'])
        return operations
        
    def set_listings(self, document_id, listings):
        self.collection.update_one({"_id": ObjectId(document_id)}, {"$set": {"listings": listings}})
    
    def set_result(self, document_id, result):
        self.collection.update_one({"_id": ObjectId(document_id)}, {"$set": {"success": result}})

    def delete_operation(self, document_id):
        # Convert the document_id back to ObjectId
        object_id = ObjectId(document_id)
        self.collection.delete_one({"_id": object_id})

    def get_operation_by_task_id(self, task_id):
        # task_id is a string, no need for ObjectId conversion
        operation = self.collection.find_one({"task_id": task_id})
        return operation
