from argparse import Action, BooleanOptionalAction
from os.path import basename
from sys import argv

from typing import Any, Callable, Literal, Optional, Type
from pydantic import BaseModel, ConfigDict, Field
from pydantic.fields import FieldInfo

type LogLevelStr = Literal['INFO'] | Literal['WARN'] | Literal['WARNING'] | Literal['ERROR'] | Literal['DEBUG']

ENV_VAR_PREIFX="MMH_API"

class ParserKwargs(BaseModel):
  model_config = ConfigDict(arbitrary_types_allowed=True)
  help: str
  action: str | Type | None = None
  dest: str | None = None
  type: Callable[..., Any] | None = None

class CliArgument(BaseModel):
  args: list[str]
  kwargs: ParserKwargs

class JsonSchemaExtra(BaseModel):
  cli_argument: CliArgument
  environment_var: Optional[str] = None

  # Server requires a restart for this change to take effect
  requires_restart: bool = False 

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

class ConfigModel(BaseModel):
  config_file: str = Field(
    default='./config.yaml', 
    json_schema_extra=JsonSchemaExtra(
      cli_argument=CliArgument(
        args=['--config-file'],
        kwargs=ParserKwargs(
          help='The config file to load options from'
        )
      ),
      environment_var='CONFIG_FILE'
    ).model_dump()
  )
  destination: str | None = Field(default=None, json_schema_extra=JsonSchemaExtra(
    cli_argument=CliArgument(
      args=['-d', '--destination'],
      kwargs=ParserKwargs(
        help="Base path to store output (ripped) files.  Subdirectories are added here for library, media type, and title"
      )
    ),
    environment_var='DESTINATION',
  ).model_dump())
  source: str | None = Field(default=None, json_schema_extra=JsonSchemaExtra(
    cli_argument=CliArgument(
      args=['-s', '--source'],
      kwargs=ParserKwargs(
        help="The source to rip from, in a format which `makemkvcon` expects (e.g. dev:<device node>, disk:<index>, iso:<iso file>, etc.)"
      )
    )
  ).model_dump())
  tmdb_token: str | None = Field(default=None, json_schema_extra=JsonSchemaExtra(
    cli_argument=CliArgument(
      args=['--tmdb-token'],
      kwargs=ParserKwargs(
        help='Your API token for TMDB'
      )
    )
  ).model_dump())
  makemkvcon_path: str | None = Field(default=None, json_schema_extra=JsonSchemaExtra(
    cli_argument=CliArgument(
      args=['--makemkvcon-path'],
      kwargs=ParserKwargs(
        help='The path to makemkvcon'
      )
    )
  ).model_dump())
  log_level: LogLevelStr = Field(default='INFO', json_schema_extra=JsonSchemaExtra(
    requires_restart=True,
    cli_argument=CliArgument(
      args=['--log-level'],
      kwargs=ParserKwargs(
        help="The log level to use, options include ERROR, INFO, WARNING, and DEBUG (Default: INFO)"
      )
    )
  ).model_dump())
  log_file: str = Field(default=None, json_schema_extra=JsonSchemaExtra(
    requires_restart=True,
    cli_argument=CliArgument(
      args=['--log-file'],
      kwargs=ParserKwargs(
        help="The log file to store logs in"
      )
    )
  ).model_dump())
  temp_prefix: str | None = Field(default=None, json_schema_extra=JsonSchemaExtra(
    cli_argument=CliArgument(
      args=['--temp-prefix'],
      kwargs=ParserKwargs(
        help="Temporary location where ripped files are stored before they are sorted"
      )
    )
  ).model_dump())
  frontend: str | None = Field(default=None, json_schema_extra=JsonSchemaExtra(
    requires_restart=True,
    cli_argument=CliArgument(
      args=['--frontend'],
      kwargs=ParserKwargs(
        help="The address of the frontend (used for CORS mostly)"
      )
    )
  ).model_dump())
  listen_port: int = Field(default=4000, json_schema_extra=JsonSchemaExtra(
    requires_restart=True,
    cli_argument=CliArgument(
      args=['--listen-port'],
      kwargs=ParserKwargs(
        help='The port to listen on for requests',
        type=int
      )
    )
  ).model_dump())
  cors_origins: list[str] = Field(default=[], json_schema_extra=JsonSchemaExtra(
    requires_restart=True,
    cli_argument=CliArgument(
      args=['--cors-origin'],
      kwargs=ParserKwargs(
        help='Additional CORS origins to trust (for instance if the frontend is accessible via different IPs or hostnames)',
        action='append',
        dest='cors_origins'
      )
    )
  ).model_dump())
  ui_path: str | None = Field(default=None, json_schema_extra=JsonSchemaExtra(
    cli_argument=CliArgument(
      args=['--ui-path'],
      kwargs=ParserKwargs(
        help="The path to the source of compiled UI files"
      )
    )
  ).model_dump())
  pid_file: str | None = Field(default=f'{basename(argv[0])}.pid', json_schema_extra=JsonSchemaExtra(
    cli_argument=CliArgument(
      args=['--pid-file'],
      kwargs=ParserKwargs(
        help="The path to the pid file (if --daemon is/was used)"
      )
    )
  ).model_dump())
  daemon: bool = Field(default=False, json_schema_extra=JsonSchemaExtra(
    cli_argument=CliArgument(
      args=['--daemon'],
      kwargs=ParserKwargs(
        action=BooleanOptionalAction,
        help="Run as a daemon (fork and return to the terminal)"
      )
    )
  ).model_dump())