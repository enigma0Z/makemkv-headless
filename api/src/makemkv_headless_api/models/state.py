
from typing import Literal

from pydantic import BaseModel

from makemkv_headless_api.models.tmdb import TMDBMovieSearchResultModel, TMDBShowSearchResultModel
from makemkv_headless_api.models.toc import TocModel

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
  library: str = None
  media: str = None
  content: str = None

class RipSortInfoModel(BaseModel):
  name: str = None
  id: str = None
  main_indexes: list[int] = None 
  extra_indexes: list[int] = None
  split_segments: list[int] = []
  id_db: str = "tmdbid"

class RipShowInfoModel(RipSortInfoModel):
  first_episode: int = None
  season_number: int = None

class ReduxRipStateModel(BaseModel):
  destination: RipDestinationModel = None
  sort_info: RipSortInfoModel | RipShowInfoModel = None
  rip_all: bool = None
  tmdb_selection: TMDBShowSearchResultModel | TMDBMovieSearchResultModel | None = None

class ReduxStateModel(BaseModel):
  rip: ReduxRipStateModel = ReduxRipStateModel()
  toc: TocModel = TocModel()

class ProgressStateModel(BaseModel):
  buffer: float | None = None
  progress: float = 0

class SocketStatusModel(BaseModel):
  current_title: int | None = None
  current_progress: list[ProgressStateModel] = []
  total_progress: ProgressStateModel = ProgressStateModel()
  current_status: StatusMessage | None = None
  total_status: StatusMessage | None = None
  rip_started: bool = False

class StateModel(BaseModel):
  redux: ReduxStateModel = ReduxStateModel()
  socket: SocketStatusModel = SocketStatusModel()