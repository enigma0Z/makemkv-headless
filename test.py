#!/usr/bin/env python3

from typing import TypedDict


class Params(TypedDict):
  foo: str
  bar: int
  baz: bool

def fn(params: Params):
  print(params)

fn(params={
})