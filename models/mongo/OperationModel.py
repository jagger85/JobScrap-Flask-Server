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
        if platform:
            query['platform'] = platform
        if user:
            query['user'] = user
        
        # Handle cursor-based pagination with sort order
        if cursor:
            cursor_obj = ObjectId(cursor)
            if sort_order == 'asc':
                query['_id'] = {'$gt': cursor_obj}
            else:
                query['_id'] = {'$lt': cursor_obj}
        
        # Determine sort direction
        sort_direction = 1 if sort_order == 'asc' else -1
        
        # Execute query
        operations = list(self.collection.find(query)
                        .sort('_id', sort_direction)
                        .limit(limit + 1))
        
        has_next = len(operations) > limit
        operations = operations[:limit]
        
        # Convert ObjectIds to strings and format response
        for op in operations:
            op['_id'] = str(op['_id'])
        
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
