#!/usr/bin/env python3

from pydantic import BaseModel


class Model(BaseModel):
  model_field: list[str]

class Impl(Model):
  impl_field: str
  def __init__(self, model_field_str: str):
    super().__init__(
      impl_field=model_field_str,
      model_field=model_field_str.split(',')
    )

    self.impl_field += "foo"

print('hello world')

v = Impl('a,b,c,d')

print(v)