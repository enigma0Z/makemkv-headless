from socket import socket, AF_INET, SOCK_DGRAM

from asyncio import create_task
from contextlib import asynccontextmanager
import logging
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.socket import socket
from src.config import CONFIG

from src.interface import get_interface, init_interface

from src.interface.async_queue_interface import AsyncQueueInterface

from . import v1

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
  # Start thread queue interface
  CONFIG.update_from_file('./config.yaml')
  logger.debug(f'Starting async queue interface with socket {socket}')
  init_interface(AsyncQueueInterface(socket))
  create_task(get_interface().run())
  yield
  # Shut down thread queue interface
  logger.info('Shutdown')

app = FastAPI(lifespan=lifespan)

cors_allow_origins = ["http://localhost:3000", *CONFIG.cors_origins ]

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