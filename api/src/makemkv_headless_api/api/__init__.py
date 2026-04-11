from socket import socket, AF_INET, SOCK_DGRAM

from asyncio import create_task
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from makemkv_headless_api.api.socket import socket

from makemkv_headless_api.config import CONFIG
from makemkv_headless_api.interface import get_interface, init_interface

from makemkv_headless_api.interface.async_queue_interface import AsyncQueueInterface

from . import v1

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
  # Start thread queue interface
  logger.debug(f'Starting async queue interface with socket {socket}')
  init_interface(AsyncQueueInterface(socket))
  create_task(get_interface().run())
  yield
  # Shut down thread queue interface
  logger.info('Shutdown')

app = FastAPI(lifespan=lifespan)

cors_allow_origins = [CONFIG.frontend, *CONFIG.cors_origins]

logger.info(f'Loaded config: {CONFIG}')
logger.info(f'Allowed CORS Origins: {cors_allow_origins}')

# try:
#   logger.debug(f'')
#   s = socket(AF_INET, SOCK_DGRAM) 
#   s.connect(("169.254.255.255", 80))
#   ip = s.getsockname()[0]
#   s.close()
#   logger.debug(f'adding {ip} to allowed origins')
#   cors_allow_origins.append(f'http://{ip}:3000')
# except:
#   logger.error(f'Failed to determine origin ip for cors')
#   pass

app.add_middleware(
  CORSMiddleware,
  # TODO: Add routable IPs
  allow_origins=cors_allow_origins,
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*']
)

app.include_router(prefix="/api", router=v1.router)

@app.get('/')
async def root():
  return "OK"