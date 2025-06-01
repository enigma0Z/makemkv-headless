
from flask import Flask

from api.thread_queue_interface import ThreadQueueInterface

class State:
    def __init__(self):
        self.ripping = False
        self.sorting = False
        self.copying = False 
    
STATE = State()
INTERFACE = ThreadQueueInterface()
API = Flask(__name__)