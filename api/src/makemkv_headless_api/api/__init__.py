import os

from importlib import resources

from pathlib import Path
from socket import socket

from asyncio import create_task
from contextlib import asynccontextmanager
import logging
from traceback import format_exc
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import FileResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette import status 

from makemkv_headless_api import ui
from makemkv_headless_api.api.socket import socket

from makemkv_headless_api.api.state import STATE
from makemkv_headless_api.config import CONFIG
from makemkv_headless_api.interface import get_interface, init_interface

from makemkv_headless_api.interface.async_queue_interface import AsyncQueueInterface
from makemkv_headless_api.models.socket import ErrorMessage
from makemkv_headless_api.models.state import ErrorStateModel

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
  print('exception handler', request, ex, ex.__class__)
  if request.url.path.startswith('/api'):
    # Store error state
    STATE.error = ErrorStateModel(
      path=request.url.path,
      message=str(ex),
      traceback=format_exc(-3).split('\n'),
    )
    logger.error("API Error", exc_info=True)
    get_interface().send(ErrorMessage(error=STATE.error))
    return await http_exception_handler(request, StarletteHTTPException(500, STATE.error.model_dump(mode='json')))
  elif isinstance(ex, FileNotFoundError):
    return await http_exception_handler(request, StarletteHTTPException(404, f'{ex}'))
  elif isinstance(ex, RuntimeError):
    return await http_exception_handler(request, StarletteHTTPException(500, f'{ex}'))
  elif isinstance(ex, StarletteHTTPException):
    return await http_exception_handler(request, ex)

@app.get('/')
@app.get('/{path:path}')
async def arbitrary_file(path: str | None = None):
  if path is None or path == '':
    path = 'index.html'
  # Configured UI path
  if CONFIG.ui_path is not None:
    served_file = os.path.join(CONFIG.ui_path, path)
    if os.path.exists(served_file):
      return FileResponse(served_file)
  # Configured external UI
  elif CONFIG.frontend is not None:
    return RedirectResponse(
      '/'.join(CONFIG.frontend, path),
      status_code=status.HTTP_302_FOUND
    )
  # Use bundled UI
  else:
    with resources.as_file(resources.files(ui) / 'dist' / path) as module_file:
      if module_file.exists():
        return FileResponse(module_file)

  raise StarletteHTTPException(404, f'Error loading file at {path}')