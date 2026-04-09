
from typing import Type, TypedDict

from pydantic import BaseModel

from .NamedHeuristic import NamedHeuristic

HeuristicRegistry: dict[str, NamedHeuristic] = {}

def register_heuristic(heuristic: Type[NamedHeuristic]):
	HeuristicRegistry[heuristic.__name__] = heuristic

def get_all_heuristics():
	return HeuristicRegistry

def get_heuristic(name):
	return HeuristicRegistry[name]