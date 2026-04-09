
from os import stat_result
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class Match(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    path: Path
    stat: stat_result