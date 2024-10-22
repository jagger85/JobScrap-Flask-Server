import os
from dotenv import load_dotenv
from transitions import Machine

load_dotenv()

# Define the possible states
states = ['idle', 'requesting_data', 'waiting_data', 'processing_data', 'sending_result', 'error']

# TRANSITIONS
# A transition happens when a trigger is called
# Each transition has a source (current state) and a dest (destination state)
# Error_occurred: Moves the machine to error from any state ('*' represents any state)

transitions = [
{'trigger': 'init','source':'*','dest':'requesting_data'},
{'trigger': 'request_data', 'source':'idle','dest':'waiting_data'},
{'trigger': 'wait_data', 'source':'requesting_data','dest':'processing_data'},
{'trigger': 'process_data', 'source':'waiting_data','dest':'sending_result'},
{'trigger': 'error_occurred', 'source':'*','dest':'error'},
]

#URLS
## base url for requests
## base url for snashot state
## base url to request snapshot 

class BrightPioneer():
    
    def __init__(self):
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='idle')
        self.api_key = os.getenv('BRIGHT')
        self.snapshot_id = None
        self.params = None
        self.init()

# STATE HANDLERS
# These methods are automatically called when the machine enters specific states. 

    def on_enter_requesting_data(self):
        pass

    def on_enter_waiting_data(self):
        pass

    def on_enter_processing_data(self):
        pass

    def on_enter_sending_result(self):
        pass

    def on_enter_error(self):
        pass


# TASK METHODS
# These methods handle the actual work for each step
   
    def request_data(self):
        pass
    
    def wait_for_data(self):
        pass

    def process_data(self):
        pass
    
    def send_data(self):
        pass


if __name__ == "__main__":
    probe = BrightPioneer()
