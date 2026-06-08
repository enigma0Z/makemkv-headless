from argparse import ArgumentParser, Namespace
import json
import logging
import yaml
from dotenv import dotenv_values

from os.path import abspath

from makemkv_headless.models.config import ConfigModel, JsonSchemaExtra

class Config(ConfigModel):
  _parser: ArgumentParser

  def __str__(self):
    return f'{super().model_dump(mode='json')}'

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  @staticmethod
  def initialize_parser(parser: ArgumentParser, opts: list[str] | None = None):
    '''
    Initialze an argparse parser from the config base model

    Args:    
      * `parser`: The ArgumentParser instance to modify
      * `opts`: An optional list[str] of args to include for the parser.
        If left unspecified, all config items have args generated for the parser.
    '''
    for (key, value) in ConfigModel.model_fields.items():
      # If opts are listed, skip those in the config which are not.
      if opts is not None and key not in opts:
        continue

      # Load JSON schema extra from the config file
      json_schema_extra = JsonSchemaExtra.model_validate(value.json_schema_extra)
      args = json_schema_extra.cli_argument.args
      kwargs = json_schema_extra.cli_argument.kwargs

      # Get parser args from the config item
      parser.add_argument(*args, **kwargs.model_dump())

  def load(self, opts: Namespace):
    # Load config file into opts
    if ('config_file' in opts and opts.config_file is not None):
      self.config_file = opts.config_file

    self.update_from_file(self.config_file)

    for key in self.__class__.model_fields:
      try:
        opt = getattr(opts, key)
      except AttributeError:
        continue

      if opt is not None:
        setattr(CONFIG, key, opt)

  def update(
      self, /, *, config_model: ConfigModel | None = None, **kwargs: dict | ConfigModel
  ) -> bool:
    '''
    Sets the specified config values.  Returns true if the update requires a
    server restart
    '''
    require_restart = False
    if config_model is not None:
      for key, value in config_model.model_dump().items():
        if value != ConfigModel.model_fields[key].default:
          json_schema_extra = JsonSchemaExtra.model_validate(ConfigModel.model_fields[key].json_schema_extra)
          if json_schema_extra.requires_restart:
            require_restart = True
          setattr(self, key, value)
    else:
      for key in kwargs:
        self.__setattr__(key, kwargs[key])

    return require_restart

  def update_from_file(self, config_file: str = None):
    if (config_file == None):
      config_file = self.config_file
    else:
      self.config_file = config_file

    try:
      if self.config_file is not None:
        if config_file.endswith('.json'):
          self.update_from_json(self.config_file)
        elif config_file.endswith('.yaml'):
          self.update_from_yaml(self.config_file)
    except FileNotFoundError:
      print(f'Could not load config file {self.config_file}, continuing...')

  def update_from_json(self, config_file: str):
    with open(config_file, 'r') as file:
      self.update(**json.loads(file.read()))

  def update_from_yaml(self, config_file: str):
    with open(config_file, 'r') as file:
      self.update(**yaml.safe_load(file)) 
  
  def update_from_dotenv(self, dotenv_file: str):
    dotenv_file_values = dotenv_values(dotenv_file)
    for key, value in self.__class__.model_fields.items():
      json_schema_extra = JsonSchemaExtra.model_validate(value.json_schema_extra)
      environment_var = json_schema_extra.environment_var
      if environment_var in dotenv_file_values:
        if value.annotation == list[str]:
          setattr(self, key, dotenv_file_values[environment_var].split(','))  # pyright: ignore[reportOptionalMemberAccess]
        else:
          setattr(self, key, dotenv_file_values[environment_var])

  def get_log_level(self) -> int:
    if self.log_level == 'ERROR':
      return logging.ERROR

    if self.log_level == 'WARN' or self.log_level == 'WARNING':
      return logging.WARNING

    if self.log_level == 'INFO':
      return logging.INFO

    if self.log_level == 'DEBUG':
      return logging.DEBUG

    return logging.INFO

  def normalize_paths(self):
    if self.temp_prefix is not None and self.temp_prefix.startswith('.'):
      self.temp_prefix = abspath(self.temp_prefix) + "/"

    if self.destination is not None and self.destination.startswith('.'):
      self.destination = abspath(self.destination) + "/"

  def write_config_file(self):
    self.normalize_paths()
    logging.info(f"Writing config file with data {self.model_dump()}")
    if self.config_file is not None:
      with open(self.config_file, 'w') as file:
        if self.config_file.endswith('.json'):
          print(self.model_dump(mode='json'), file=file)
        elif self.config_file.endswith('.yaml'):
          print(yaml.dump(self.model_dump()), file=file)
    
  def env_file_lines(self) -> list[str]:
    env_file_lines = []
    for key, value in ConfigModel.model_fields.items():
      json_schema_extra = JsonSchemaExtra.model_validate(value.json_schema_extra)
      config_value = self.model_dump()[key]
      if isinstance(config_value, list):
        config_value = ','.join(config_value)
      elif config_value is None:
        config_value = ''
      env_file_lines.append(f'{json_schema_extra.environment_var}={config_value}')

    return env_file_lines

CONFIG = Config()