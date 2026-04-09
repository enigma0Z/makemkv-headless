from enum import StrEnum, auto, unique

@unique
class Target(StrEnum):
  MKV = auto()
  SORT = auto()
  INPUT = auto()
  STATUS = auto()
