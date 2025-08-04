

from pydantic import BaseModel


class ConfigModel(BaseModel):
  filename: str | None = None
  tmdb_token: str | None = None
  makemkvcon_path: str | None = None
  source: str | None = None
  destination: str | None  = None
  log_level: str | None = None
  temp_prefix: str | None = None
  frontend: str | None = None