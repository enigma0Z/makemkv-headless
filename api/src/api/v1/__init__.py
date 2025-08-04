from fastapi import APIRouter

from . import config
from . import disc
from . import state
from . import tmdb
from . import toc
from . import queue

router = APIRouter(prefix="/v1")
router.include_router(config.router)
router.include_router(disc.router)
router.include_router(state.router)
router.include_router(tmdb.router)
router.include_router(toc.router)
router.include_router(queue.router)
