from pydantic import BaseModel


class TMDBConfigurationModel(BaseModel):
  class ImagesModel(BaseModel):
    base_url: str
    secure_base_url: str
    backdrop_sizes: list[str]
    logo_sizes: list[str]
    poster_sizes: list[str]
    still_sizes: list[str]

  change_keys: list[str]
  images: ImagesModel

class TMDBSearchResultBaseModel(BaseModel):
  adult: bool # Common
  backdrop_path: str | None # Common
  genre_ids: list[int] # Common
  id: int # Common
  original_language: str # Common
  overview: str # Common
  popularity: float # Common
  poster_path: str | None # Common
  vote_average: float # Common
  vote_count: float # Common

class TMDBShowSearchResultModel(TMDBSearchResultBaseModel):
  origin_country: list[str]
  original_name: str
  first_air_date: str
  name: str

class TMDBMovieSearchResultModel(TMDBSearchResultBaseModel):
  original_title: str
  release_date: str
  title: str
  video: bool