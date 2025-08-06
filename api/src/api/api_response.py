
from traceback import format_exc, format_exception
from typing import Generic, Literal, TypeVar
from fastapi import HTTPException
from pydantic import BaseModel

import logging
logger = logging.getLogger(__name__)

type Status = Literal[
  "success",
  "failure",
  "started",
  "in progress",
  "done",
  "stopped",
  "error",
]

T = TypeVar('T')
class APIResponse(BaseModel, Generic[T]):
  status: Status
  data: T | None = None
  def __init__(self, status: Status, data):
    super().__init__(status=status, data=data)

class PaginatedAPIResponse(APIResponse[T]):
  page: int
  page_size: int
  num_pages: int

class APIError(APIResponse[list[str]]):
  def __init__(self, status: Status, ex: Exception):
    super().__init__(status=status, data=format_exception(ex))

class APIException(HTTPException):
  def __init__(self, status_code: int, error: APIError ):
    super().__init__(status_code, error.model_dump())
