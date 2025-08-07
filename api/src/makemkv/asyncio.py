#!/usr/bin/env python3

from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE
import re
import shlex
from time import time

import logging

from src.interface import get_interface
from src.interface.base_interface import BaseInterface
from src.interface.plaintext_interface import PlaintextInterface
from src.interface.target import Target
from src.message.rip_start_stop_message_event import RipStartStopMessageEvent
from src.models.makemkv import from_raw
from src.models.socket import RipStartStopMessage, mkv_message_from_raw
from src.threads import StoppableThread
logger = logging.getLogger(__name__)

from src.message.build_message import build_message
from src.config import CONFIG
from src.disc import wait_for_disc_inserted
from src.util import seconds_to_hms

async def rip_disc(
    source, 
    dest,
    rip_titles=['all'],
):
  interface = get_interface()
  logger.info(f'Backing up {source} to {dest}')
  interface.print(f'Backing up {source} to {dest}', target=Target.SORT)

  wait_for_disc_inserted(source, interface)

  # Do the actual rip + eject the disc when done
  for rip_title in [str(v) for v in rip_titles]:
    logger.info(f'Ripping title {rip_title}')
    interface.print(f'Ripping title {rip_title}', target=Target.SORT)
    if rip_title == "all":
      interface.send(RipStartStopMessage(index=0, state="start"))
    else:
      interface.send(RipStartStopMessage(index=int(rip_title), state="start"))

    with open('makemkv.log', 'w') as log:
      process = await create_subprocess_shell(
        shlex.join([CONFIG.makemkvcon_path, '--noscan', '--robot', '--progress=-same', 'mkv', source, rip_title, dest]),
        stdout=PIPE,
        stderr=PIPE
      )

      while not process.stdout.at_eof():
        line = (await process.stdout.readline()).decode().strip()
        interface.send(mkv_message_from_raw(line))

    interface.send(RipStartStopMessageEvent(index=rip_title, state="stop"))