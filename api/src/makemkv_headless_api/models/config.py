

import logging
from typing import Literal, Type
from pydantic import BaseModel

type LogLevelStr = Literal['INFO'] | Literal['WARN'] | Literal['WARNING'] | Literal['ERROR'] | Literal['DEBUG']

class ConfigModel(BaseModel):
  filename: str | None = None
  tmdb_token: str | None = None
  makemkvcon_path: str | None = None
  source: str | None = None
  destination: str | None  = None
  log_level: LogLevelStr = 'INFO'
  log_file: str = "api.log"
  temp_prefix: str | None = None
  frontend: str | None = None
  listen_port: int = 4000
  cors_origins: list[str] = []