
import logging
from typing import TypedDict
from deepmerge.merger import Merger
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from src.json_serializable import JSONSerializable
from src.config import CONFIG

from src.api.thread_queue_interface import ThreadQueueInterface

logger = logging.getLogger(__name__)

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
