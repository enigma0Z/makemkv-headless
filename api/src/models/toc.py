

from pydantic import BaseModel

class BaseInfoModel(BaseModel):
  fields: dict[str, str] = {}

class TrackInfoModel(BaseModel):
  stream_type: str | None = None
  stream_format: str | None = None
  stream_conversion_type: str | None = None
  stream_bitrate: str | None = None
  stream_language_code: str | None = None
  stream_language: str | None = None
  stream_detail: str | None = None
  audio_format: str | None = None
  video_resolution: str | None = None
  video_aspect_ratio: str | None = None
  video_framerate: str | None = None

class TitleInfoModel(BaseInfoModel):
  tracks: list[TrackInfoModel] = []
  chapters: int | None = None
  runtime: str | None = None
  size: str | None = None
  segments: int | None = None
  segments_map: str | None = None
  filename: str | None = None
  summary: str | None = None

class SourceInfoModel(BaseInfoModel):
  titles: list[TitleInfoModel] = []
  name: str | None = None
  name1: str | None = None
  name2: str | None = None
  name3: str | None = None

class TocModel(BaseModel):
  source: SourceInfoModel | None = None
  lines: list[str] = []