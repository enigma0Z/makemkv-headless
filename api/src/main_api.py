import logging

import uvicorn

from src.config import CONFIG

CONFIG.update_from_file('./config.yaml')

from src.api import app

logging.basicConfig(
  style='{', 
  format='{asctime} [{levelname}] {filename}:{lineno} {threadName} - {message}', 
  level=logging.DEBUG
)

logger = logging.getLogger(__name__)
logger.info(f'Starting app {app}')

if __name__ == '__main__':
  uvicorn.run(app, host="0.0.0.0", port=4000) 