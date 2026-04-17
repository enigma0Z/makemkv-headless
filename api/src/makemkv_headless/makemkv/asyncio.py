#!/usr/bin/env python3

import logging

from makemkv_headless.interface import get_interface
from makemkv_headless.interface.target import Target
from makemkv_headless.models.socket import RipStartStopMessage, mkv_message_from_raw
logger = logging.getLogger(__name__)

from makemkv_headless.config import CONFIG
from makemkv_headless.disc import wait_for_disc_inserted
from makemkv_headless.util import cmd

async def rip_disc(
    source, 
    dest,
    rip_titles=['all'],
):
  interface = get_interface()
  logger.debug(f'rip_disc() interface {interface}')
  logger.info(f'Backing up {source} to {dest}')
  interface.print(f'Backing up {source} to {dest}', target=Target.SORT)

  wait_for_disc_inserted(source, interface)

  # Do the actual rip + eject the disc when done
  for rip_title in [str(v) for v in rip_titles]:
    logger.info(f'Ripping title {rip_title}')
    interface.print(f'Ripping title {rip_title}', target=Target.SORT)

    interface.send(RipStartStopMessage(index=0 if rip_title == 'all' else int(rip_title), state="start"))

    def send_mkv_message(line: str):
      interface.send(mkv_message_from_raw(line))

    await cmd(CONFIG.makemkvcon_path, '--noscan', '--robot', '--progress=-same', 'mkv', source, rip_title, dest, callback=send_mkv_message)

    interface.send(RipStartStopMessage(index=0 if rip_title == 'all' else int(rip_title), state="stop"))