
from pydantic import BaseModel

from src.message.progress_message_event import StatusMessage
from src.models.toc import TOCModel


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

class ReduxStateModel(BaseModel):
  rip: ReduxRipStateModel = ReduxRipStateModel()
  toc: TOCModel = TOCModel()

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