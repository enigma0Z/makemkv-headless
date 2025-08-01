
from typing import Literal
from src.json_serializable import JSONSerializable

type Status = Literal[
    "success",
    "failure",
    "started",
    "in progress",
    "done",
    "stopped",
    "error",
]

class APIResponse(JSONSerializable):
    def __init__(self, status: Status, data=None, **_kwargs):
        self.status = status
        self.data = data

class PaginatedAPIResponse(APIResponse):
    def __init__(self, page, page_size, num_pages, status: Status, data=None, **kwargs):
      self.page = page,
      self.page_size = page_size
      self.num_pages = num_pages
      super().__init__(status, data)