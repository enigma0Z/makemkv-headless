import os

from socket import socket

from asyncio import create_task
from contextlib import asynccontextmanager
import logging
from traceback import format_exc
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from makemkv_headless_api.api.socket import socket

from makemkv_headless_api.api.state import STATE
from makemkv_headless_api.config import CONFIG
from makemkv_headless_api.interface import get_interface, init_interface

from makemkv_headless_api.interface.async_queue_interface import AsyncQueueInterface
from makemkv_headless_api.models.state import ErrorStatusModel

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

@app.exception_handler(Exception)
async def exception_handler(request: Request, ex: Exception):
  if request.url.path.startswith('/api'):
    # Store error state
    STATE.error = ErrorStatusModel(
      path=request.url.path,
      message=str(ex),
      traceback=format_exc(-3).split('\n'),
    )
    logger.error("API Error", exc_info=True)
    return await http_exception_handler(request, StarletteHTTPException(500, STATE.error.model_dump(mode='json')))
  elif isinstance(ex, StarletteHTTPException):
    return await http_exception_handler(request, ex)
  else:
    raise ex

@app.get('/')
async def index():
  return FileResponse(os.path.join(CONFIG.ui_path, 'index.html'))

@app.get('/{path:path}')
async def arbitrary_file(path: str):
  served_file = os.path.join(CONFIG.ui_path, path)
  if os.path.exists(served_file):
    return FileResponse(served_file)
  else:
    return HTTPException(404)