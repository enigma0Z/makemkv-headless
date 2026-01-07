#!/usr/bin/env python3

import logging

from src.interface import get_interface
from src.interface.target import Target
from src.message.rip_start_stop_message_event import RipStartStopMessageEvent
from src.models.socket import RipStartStopMessage, mkv_message_from_raw
logger = logging.getLogger(__name__)

from src.config import CONFIG
from src.disc import wait_for_disc_inserted
from src.util import cmd

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
    if rip_title == "all":
      interface.send(RipStartStopMessage(index=0, state="start"))
    else:
      interface.send(RipStartStopMessage(index=int(rip_title), state="start"))

    def send_mkv_message(line: str):
      interface.send(mkv_message_from_raw(line))

    await cmd(CONFIG.makemkvcon_path, '--noscan', '--robot', '--progress=-same', 'mkv', source, rip_title, dest, callback=send_mkv_message)

    interface.send(RipStartStopMessageEvent(index=rip_title, state="stop"))