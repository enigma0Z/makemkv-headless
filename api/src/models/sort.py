
from pydantic import BaseModel


class SortInfoModel(BaseModel):
    name: str
    id: str
    main_indexes: list[int]
    extra_indexes: list[int]
    split_segments: list[int] = []
    id_db: str = 'tmdbid'

class ShowInfoModel(SortInfoModel):
    season_number: int
    first_episode: int