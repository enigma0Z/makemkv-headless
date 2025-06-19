#!/usr/bin/env python3

def generate_CINFO(format='raw'):
  lines = [
    f'CINFO:1,6206,"media"',
    f'CINFO:2,0,"name1"',
    f'CINFO:30,0,"name2"',
    f'CINFO:31,6119,"<b>Source information</b><br>"',
    f'CINFO:32,0,"name3"',
    f'CINFO:33,0,"0"',
  ]

  return lines

def generate_TINFO(format='raw', title_index=0):
  lines = [
    f'TINFO:{title_index},8,0,"2"',
    f'TINFO:{title_index},9,0,"0:23:17"',
    f'TINFO:{title_index},10,0,"688.6 MB"',
    f'TINFO:{title_index},11,0,"722130944"',
    f'TINFO:{title_index},24,0,"08"',
    f'TINFO:{title_index},25,0,"2"',
    f'TINFO:{title_index},26,0,"1,2"',
    f'TINFO:{title_index},27,0,"filename.mkv"',
    f'TINFO:{title_index},30,0,"summary"',
    f'TINFO:{title_index},31,6120,"<b>Title information</b><br>"',
    f'TINFO:{title_index},33,0,"0"',
    f'TINFO:{title_index},49,0,"B2"',
  ]

  return lines

def generate_SINFO(format='raw', title_index=0, stream_indexes = [0, 1, 2]):
  lines = [
    f'SINFO:{title_index},{stream_indexes[0]},1,6201,"Video"',
    f'SINFO:{title_index},{stream_indexes[0]},5,0,"V_MPEG2"',
    f'SINFO:{title_index},{stream_indexes[0]},6,0,"Mpeg2"',
    f'SINFO:{title_index},{stream_indexes[0]},7,0,"Mpeg2"',
    f'SINFO:{title_index},{stream_indexes[0]},13,0,"9.8 Mb/s"',
    f'SINFO:{title_index},{stream_indexes[0]},19,0,"720x480"',
    f'SINFO:{title_index},{stream_indexes[0]},20,0,"4:3"',
    f'SINFO:{title_index},{stream_indexes[0]},21,0,"29.97 (30000/1001)"',
    f'SINFO:{title_index},{stream_indexes[0]},22,0,"0"',
    f'SINFO:{title_index},{stream_indexes[0]},30,0,"Mpeg2"',
    f'SINFO:{title_index},{stream_indexes[0]},31,6121,"<b>Track information</b><br>"',
    f'SINFO:{title_index},{stream_indexes[0]},33,0,"0"',
    f'SINFO:{title_index},{stream_indexes[0]},38,0,""',
    f'SINFO:{title_index},{stream_indexes[0]},42,5088,"( Lossless conversion )"',

    f'SINFO:{title_index},{stream_indexes[1]},1,6202,"Audio"',
    f'SINFO:{title_index},{stream_indexes[1]},2,5091,"Stereo"',
    f'SINFO:{title_index},{stream_indexes[1]},3,0,"eng"',
    f'SINFO:{title_index},{stream_indexes[1]},4,0,"English"',
    f'SINFO:{title_index},{stream_indexes[1]},5,0,"A_AC3"',
    f'SINFO:{title_index},{stream_indexes[1]},6,0,"DD"',
    f'SINFO:{title_index},{stream_indexes[1]},7,0,"Dolby Digital"',
    f'SINFO:{title_index},{stream_indexes[1]},13,0,"192 Kb/s"',
    f'SINFO:{title_index},{stream_indexes[1]},14,0,"2"',
    f'SINFO:{title_index},{stream_indexes[1]},17,0,"48000"',
    f'SINFO:{title_index},{stream_indexes[1]},22,0,"0"',
    f'SINFO:{title_index},{stream_indexes[1]},30,0,"DD Stereo English"',
    f'SINFO:{title_index},{stream_indexes[1]},31,6121,"<b>Track information</b><br>"',
    f'SINFO:{title_index},{stream_indexes[1]},33,0,"90"',
    f'SINFO:{title_index},{stream_indexes[1]},38,0,"d"',
    f'SINFO:{title_index},{stream_indexes[1]},39,0,"Default"',
    f'SINFO:{title_index},{stream_indexes[1]},40,0,"stereo"',
    f'SINFO:{title_index},{stream_indexes[1]},42,5088,"( Lossless conversion )"',

    f'SINFO:{title_index},{stream_indexes[2]},1,6203,"Subtitles"',
    f'SINFO:{title_index},{stream_indexes[2]},3,0,"eng"',
    f'SINFO:{title_index},{stream_indexes[2]},4,0,"English"',
    f'SINFO:{title_index},{stream_indexes[2]},5,0,"S_CC608/DVD"',
    f'SINFO:{title_index},{stream_indexes[2]},6,0,"CC"',
    f'SINFO:{title_index},{stream_indexes[2]},7,0,"Closed Captions"',
    f'SINFO:{title_index},{stream_indexes[2]},13,0,"9.8 Mb/s"',
    f'SINFO:{title_index},{stream_indexes[2]},22,0,"0"',
    f'SINFO:{title_index},{stream_indexes[2]},30,0,"CC→Text English ( Lossy conversion )"',
    f'SINFO:{title_index},{stream_indexes[2]},31,6121,"<b>Track information</b><br>"',
    f'SINFO:{title_index},{stream_indexes[2]},33,0,"90"',
    f'SINFO:{title_index},{stream_indexes[2]},34,0,"Text subtitles ( Lossy conversion )"',
    f'SINFO:{title_index},{stream_indexes[2]},38,0,"d"',
    f'SINFO:{title_index},{stream_indexes[2]},39,0,"Default"',
    f'SINFO:{title_index},{stream_indexes[2]},41,0,"Text"',
    f'SINFO:{title_index},{stream_indexes[2]},42,5087,"( Lossy conversion )"',
  ]

  return lines