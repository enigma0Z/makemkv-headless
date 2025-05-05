#!/usr/bin/env python3

from unittest import TestCase

from test.data.toc_test_data import generate_CINFO, generate_TINFO, generate_SINFO
from toc import TOC, TrackInfo, format_records

class TOCTest(TestCase):
  def test_format_records(self):
    [record] = format_records(['CINFO:2,0,"title: subtitle"'])
    print(record)
    self.assertEqual('CINFO', record[0], "Record type is split as expected")
    self.assertEqual('"title: subtitle"', record[3], "Colons after the first colon are ignored")
    self.assertEqual(4, len(record))

  def test_TOC_from_disc(self):
    # TOC.get_from_disc
    pass

  def test_TOC_from_list(self):
    # TOC.get_from_list
    list_toc = TOC()
    list_toc.get_from_list(generate_CINFO() + generate_TINFO() + generate_SINFO())

    self.assertEqual('name1', list_toc.source.name)
    self.assertEqual('name1', list_toc.source.name1)
    self.assertEqual('name2', list_toc.source.name2)
    self.assertEqual('name3', list_toc.source.name3)
    self.assertEqual('media', list_toc.source.media)

    self.assertEqual('filename.mkv', list_toc.source.titles[0].filename)
    self.assertEqual('summary', list_toc.source.titles[0].summary)
    self.assertEqual('0:23:17', list_toc.source.titles[0].runtime)
    self.assertEqual('1,2', list_toc.source.titles[0].segments_map)

    self.assertEqual('V_MPEG2', list_toc.source.titles[0].tracks[0].stream_format)
    self.assertEqual('A_AC3', list_toc.source.titles[0].tracks[1].stream_format)
    self.assertEqual('S_CC608/DVD', list_toc.source.titles[0].tracks[2].stream_format)

    self.assertEqual('Mpeg2', list_toc.source.titles[0].tracks[0].stream_detail)
    self.assertEqual('DD Stereo English', list_toc.source.titles[0].tracks[1].stream_detail)
    self.assertEqual('CC→Text English ( Lossy conversion )', list_toc.source.titles[0].tracks[2].stream_detail)

    self.assertEqual('720x480', list_toc.source.titles[0].tracks[0].video_resolution)
    self.assertEqual('4:3', list_toc.source.titles[0].tracks[0].video_aspect_ratio)
    self.assertEqual('29.97 (30000/1001)', list_toc.source.titles[0].tracks[0].video_framerate)

    self.assertEqual('Stereo', list_toc.source.titles[0].tracks[1].audio_format)