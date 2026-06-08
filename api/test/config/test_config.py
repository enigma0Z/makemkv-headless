from argparse import Namespace
import os
import shutil
import tempfile

from dotenv import dotenv_values
from makemkv_headless.api import cors_allow_origins
from makemkv_headless.config import CONFIG
import pytest

def test_config_env_vars():
  CONFIG.load(Namespace(config_file=None))
  env_file_lines = CONFIG.env_file_lines()
  assert 'MMH_API_CONFIG_FILE=' in env_file_lines

def test_config_list_env_vars():
  CONFIG.load(Namespace(config_file=None, cors_origins=['one', 'two']))
  env_file_lines = CONFIG.env_file_lines()
  assert 'MMH_API_CORS_ORIGINS=one,two' in env_file_lines

def test_config_list_load_env():
  env_file_contents = '\n'.join([
    'MMH_API_CORS_ORIGINS=one,two',
    'MMH_API_LISTEN_PORT=1234'
  ])
  temp_dir = tempfile.mkdtemp()
  env_file = os.path.join(temp_dir, 'test.env')
  with open(env_file, 'w') as file:
    file.writelines(env_file_contents)

  CONFIG.update_from_dotenv(env_file)
  shutil.rmtree(temp_dir)

  assert CONFIG.listen_port == '1234'
  assert CONFIG.cors_origins == ['one', 'two']