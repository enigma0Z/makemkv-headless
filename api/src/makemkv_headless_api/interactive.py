#!/usr/bin/env python3

from src.interface.base_interface import BaseInterface
from src.interface.plaintext_interface import PlaintextInterface
from src.rip_titles.interactive import rip_movie_interactive, rip_show_interactive

def interactive_rip(
    source, destination,
    interface: BaseInterface = PlaintextInterface(),
    **kwargs
  ):
  library_choices = ['kids', 'main']
  library_choices_casefold = [choice.casefold() for choice in library_choices]
  library = 'main'

  media_choices = ['blu-ray', 'dvd']
  media_choices_casefold = [choice.casefold() for choice in media_choices]
  media = None

  content_choices = ['show', 'movie']
  content_choices_casefold = [choice.casefold() for choice in content_choices]
  content = None

  rip_args = {}

  while True:
    library = interface.get_input(
      'Should this go into the Main or Kids library?', 
      library, 
      lambda v: 
        v.casefold() in [choice.casefold() for choice in library_choices_casefold]
    )

    media = interface.get_input(
      'Is this Blu-Ray or DVD?', 
      media, 
      lambda v: 
        v.casefold() in [choice.casefold() for choice in media_choices_casefold]
    )

    interface.print(f'Media: {media}', target=Target.INPUT)

    content = interface.get_input(
      'Is this a show or movie?', 
      content, 
      lambda v: 
        v.casefold() in [choice.casefold() for choice in content_choices_casefold]
    )

    media = media_choices[media_choices_casefold.index(media.casefold())]
    old_content = content
    content = content_choices[content_choices_casefold.index(content.casefold())]
    if (content != old_content):
      rip_args = {}

    new_dest_dir = os.path.join(destination, library, content + 's', media)
    interface.print(new_dest_dir, target=Target.INPUT)

    if content.casefold() == 'show':
      rip_args = rip_show_interactive(
        source, 
        new_dest_dir, 
        **kwargs,
        **rip_args, 
        batch=False, 
        interface=interface
      )

    elif content.casefold() == 'movie':
      rip_args = rip_movie_interactive(
        source, 
        new_dest_dir, 
        **kwargs,
        **rip_args, 
        batch=False,
        interface=interface
      )
