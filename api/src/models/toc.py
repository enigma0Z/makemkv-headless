

from pydantic import BaseModel

class BaseInfoModel(BaseModel):
  fields: dict[str, str] = {}

class TrackInfoModel(BaseModel):
  stream_type: str | None
  stream_format: str | None
  stream_conversion_type: str | None
  stream_bitrate: str | None
  stream_language_code: str | None
  stream_language: str | None
  stream_detail: str | None
  audio_format: str | None
  video_resolution: str | None
  video_aspect_ratio: str | None
  video_framerate: str | None

class TitleInfoModel(BaseInfoModel):
  tracks: list[TrackInfoModel]
  chapters: int
  runtime: str
  size: str
  segments: int
  segments_map: str
  filename: str
  summary: str

class SourceInfoModel(BaseInfoModel):
  titles: list[TitleInfoModel]
  name: str | None
  name1: str | None
  name2: str | None
  name3: str | None

class TOCModel(BaseModel):
  source: SourceInfoModel