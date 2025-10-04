import logging
import uvicorn

from sys import exit
from src.config import CONFIG

CONFIG.update_from_file('./config.yaml')

logging.basicConfig(
  style='{', 
  format='{asctime} [{levelname}] {filename}:{lineno} {threadName} - {message}', 
  level=logging.DEBUG,
  filename='api.log'
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
  from src.api import app
  logger.info(f'Starting app {app}')
  uvicorn.run(app, host="0.0.0.0", port=4000) 