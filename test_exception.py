#!/usr/bin/env python3

import deepmerge

merger = deepmerge.merger.Merger( [(dict, "merge")], ["override"], ["override"])

left = {
  "a": 1, 
  "b": 2, 
  "a_list": [1,2,3],
  "a_dict": {
    "d": 1,
    "e": 2,
    "f": 3
  }
}

right = {
  "b": 3, 
  "c": 4, 
  "a_list": [4,5,6],
  "a_dict": {
    "f": 4,
    "g": 5,
    "h": 6
  }
}

print(deepmerge.conservative_merger.merge(left, right))
print(merger.merge(left, right))