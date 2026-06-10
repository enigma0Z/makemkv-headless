
from typing import Literal

from pydantic import BaseModel

from makemkv_headless.models.tmdb import TMDBMovieSearchResultModel, TMDBShowSearchResultModel
from makemkv_headless.models.toc import TocStateModel

type StatusMessage = Literal[
  "Scanning CD-ROM devices",
  "Opening DVD disc",
  "Processing title sets",
  "Scanning contents",
  "Processing titles",
  "Decrypting data",
  "Saving all titles to MKV files",
  "Analyzing seamless segments",
  "Saving to MKV file"
]

class RipDestinationModel(BaseModel):
  library: str | None = None
  media: str | None = None
  content: str | None = None

class RipSortInfoModel(BaseModel):
  name: str | None = None
  id: str | None = None
  main_indexes: list[int] | None = None 
  extra_indexes: list[int] | None = None
  split_segments: list[int] | None = []
  id_db: str = "tmdbid"

class RipShowInfoModel(RipSortInfoModel):
  first_episode: int | None = None
  season_number: int | None = None

class RipStateModel(BaseModel):
  destination: RipDestinationModel | None = None
  sort_info: RipSortInfoModel | RipShowInfoModel | None = None
  rip_all: bool | None = None
  tmdb_selection: TMDBShowSearchResultModel | TMDBMovieSearchResultModel | None = None

class ProgressStateModel(BaseModel):
  buffer: float | None = None
  progress: float = 0

class SocketStateRipModel(BaseModel):
  current_title: int | None = None
  current_progress: list[ProgressStateModel] = []
  total_progress: ProgressStateModel = ProgressStateModel()
  current_status: StatusMessage | None = None
  total_status: StatusMessage | None = None
  started: bool = False

class SocketStateModel(BaseModel):
  rip: SocketStateRipModel = SocketStateRipModel()
  connected: bool = False
  message: list[str] = []

class ErrorStateModel(BaseModel):
  path: str
  message: str | BaseModel | None = None
  traceback: list[str] | None = None

class StateModel(BaseModel):
  rip: RipStateModel = RipStateModel()
  toc: TocStateModel = TocStateModel()
  socket: SocketStateModel = SocketStateModel()
  error: ErrorStateModel | None = None