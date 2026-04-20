
from os import stat_result
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from .NamedHeuristic import NamedHeuristic
from .Match import Match

class MatchSet(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    heuristic: NamedHeuristic
    match_key: Path
    matches: list[Match] = []
