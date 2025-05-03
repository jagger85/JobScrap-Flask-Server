from dotenv import load_dotenv
from enum import StrEnum
import os 

load_dotenv()


redis_celery_db=0
redis_redbeat_db=1
redis_websocket_db=2

environment = {
    "bright_key": os.getenv('BRIGHT_API_KEY'),

    "backend_port": os.getenv('BACKEND_PORT'),
    "backend_host": os.getenv('BACKEND_HOST'),
    "jwt_secret": os.getenv('JWT_SECRET_KEY'),

    "environment": os.getenv('ENVIRONMENT'),
    "remote_ip": os.getenv('REMOTE_UI_IP'),

    "mongo_user": os.getenv('MONGO_USER'),
    "mongo_password": os.getenv('MONGO_PASSWORD'),

    "redis_host": os.getenv("REDIS_HOST"),
    "redis_port": int(os.getenv("REDIS_PORT")),


    "redis_celery_db":redis_celery_db,
    "redis_redbeat_db":redis_redbeat_db,
    "redis_websocket_db":redis_websocket_db,

    "redis_redbeat_url": f'redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/{redis_redbeat_db}',
    "celery_broker_url":f'redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/{redis_celery_db}',
    "celery_result_backend": f'redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/{redis_celery_db}',
}

kalibrr_url = "https://www.kalibrr.com/home/co/Philippines/i/it-and-software?sort=Freshness"
kalibrr_api_url = "https://www.kalibrr.com/kjs/job_board/search"
jobstreet_url = "https://ph.jobstreet.com"

class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class DateRange(StrEnum):
    PAST_24_HOURS = "Past 24 hours"
    PAST_WEEK = "Past week"
    PAST_15_DAYS = "Past 15 days"
    PAST_MONTH = "Past month"

class MessageType(StrEnum):
    HEARTBEAT = "heartbeat" 
    PLATFORM_STATE = "platform_states"
    INFO = "info"
    WARNING = 'warning'
    ERROR = 'error'
    PROGRESS = 'progress'
    DEBUG = 'debug'

class PlatformStates(StrEnum):
    PROCESSING = "Processing"  
    COMPLETED = "Completed"   
    ERROR = "Error"

class Platforms(StrEnum):
    KALIBRR = "Kalibrr"
    JOBSTREET = "Jobstreet"
    INDEED = "Indeed"
    LINKEDIN = "LinkedIn"