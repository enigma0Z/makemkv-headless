
import logging
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from config import CONFIG
from .thread_queue_interface import ThreadQueueInterface

logger = logging.getLogger(__name__)

class State:
    def __init__(self):
        self.ripping = False
        self.sorting = False
        self.copying = False 
    
STATE = State()

API = Flask(__name__)
SOCKET = SocketIO()
INTERFACE = ThreadQueueInterface(SOCKET)

def start_api():
    logger.info('Initializing socket')
    SOCKET.init_app(API, cors_allowed_origins=CONFIG.frontend)

    logger.info('Initializing CORS')
    CORS(API, resources={r"/api/*": {"origins": CONFIG.frontend}})

    logger.info('Starting queue thread')
    INTERFACE.run()

    logger.info('Launching flask app')
    SOCKET.run(API, port=4000)
