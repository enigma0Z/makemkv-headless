
from asyncio import create_task
from contextlib import asynccontextmanager
import logging
from fastapi import APIRouter, FastAPI

from src.config import CONFIG

from src.interface import get_interface, init_interface

from src.interface.async_queue_interface import AsyncQueueInterface

from . import v1

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
  # Start thread queue interface
  CONFIG.update_from_file('./config.yaml')
  init_interface(AsyncQueueInterface())
  create_task(get_interface().run())
  yield
  # Shut down thread queue interface
  logger.info('Shutdown')

app = FastAPI(lifespan=lifespan)
api_router = APIRouter(prefix="/api")

api_router.include_router(v1.router)

@app.get('/')
async def root():
  return "OK"

app.include_router(api_router)