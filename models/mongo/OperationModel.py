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
        return list(self.collection.find({}, {"_id": 0}))
    
    
    def get_operations(self, limit=10, cursor=None, sort_order='desc', platform=None, user=None):
        query = {}
        if cursor:
            query['_id'] = {'$lt': ObjectId(cursor)}
        if platform:
            query['platform'] = platform
        if user:
            query['user'] = user
        # Get one more than limit to determine if there's a next page
        operations = list(self.collection.find(query)
                        .sort('_id', -1 if sort_order == 'desc' else 1)  # Sort by _id descending
                        .limit(limit + 1))
        
        has_next = len(operations) > limit
        operations = operations[:limit]  # Remove the extra item
        
        # Convert ObjectIds to strings
        for op in operations:
            op['_id'] = str(op['_id'])
        
        # Only set next_cursor if we have operations and there's a next page
        next_cursor = operations[-1]['_id'] if operations and has_next else None
        
        return operations, next_cursor
        
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
