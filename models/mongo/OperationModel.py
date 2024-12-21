from .BaseModel import BaseModel
from .validate_data import validate_data
class OperationModel(BaseModel):

    REQUIRED_FIELDS = ["platform", "user", "time_range"]

    def __init__(self, db):
        super().__init__(db,"Operations")

    def create_operation(self, data):
        if validate_data(data, self.REQUIRED_FIELDS):
            return self.create(data)
    
    def get_all_operations(self):
        return list(self.collection.find({}, {"_id":0}))
