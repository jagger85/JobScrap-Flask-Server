from enum import Enum

class PlatformStates(Enum):
    IDLE = "idle"
    WAITING = "waiting"      
    PROCESSING = "processing"  
    FINISHED = "finished"   
    ERROR = "error"
