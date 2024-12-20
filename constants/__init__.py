from .date_range import DateRange
from .message_type import MessageType
from .platform_states import PlatformStates
from .platforms import Platforms
from dotenv import load_dotenv
from enum import Enum
import os 

load_dotenv()

environment = {
    "jwt_secret": os.getenv('JWT_SECRET_KEY'),
    "backend_port": os.getenv('BACKEND_PORT'),
    "backend_host": os.getenv('BACKEND_HOST'),
    "environment": os.getenv('ENVIRONMENT'),
    "flask_debug": os.getenv('FLASK_DEBUG'),
    "remote_ip": os.getenv('REMOTE_IP'),
    "bright_key": os.getenv('BRIGHT'),
    "mongo_user": os.getenv('MONGO_USER'),
    "mongo_password": os.getenv('MONGO_PASSWORD')
}

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
