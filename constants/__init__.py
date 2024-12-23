from dotenv import load_dotenv
from enum import StrEnum
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
    "mongo_password": os.getenv('MONGO_PASSWORD'),
    "redis_host": os.getenv("REDIS_HOST"),
    "redis_port": os.getenv("REDIS_PORT"),
    "redis_db": os.getenv("REDIS_DB"),
    "celery_broker_url": os.getenv("CELERY_BROKER_URL"),
    "celery_result_backend": os.getenv("CELERY_RESULT_BACKEND")
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
    PROCESSING = "processing"  
    FINISHED = "finished"   
    ERROR = "error"

class Platforms(StrEnum):
    KALIBRR = "Kalibrr"
    JOBSTREET = "Jobstreet"
    INDEED = "Indeed"
    LINKEDIN = "LinkedIn"