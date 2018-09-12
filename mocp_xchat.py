""" hexchat module for controlling the Music On Console Player (MOCP)
    program.  Inspired by similar work by kubicz10
"""
# Python 3.x
from __future__ import print_function
from subprocess import check_output, call
try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

__module_name__ = "MOCP_control"
__module_version__ = "20161115"
__module_description__ = "control music from inside hexchat"
__module_author__ = "Mozai, kubicz10"


def _mocp_state():
  " returns dict() of mocp state info, or None if not running "
  infodump = check_output('mocp --info'.split()).decode('utf8')
  if infodump.find('FATAL_ERROR: The server is not running!') > -1:
    # moc isn't running
    return None
  mocstate = {}
  for line in infodump.split("\n"):
    if ':' not in line:
      continue
    fields = line.split(': ', 2)
    if fields[1].strip():
      mocstate[fields[0]] = fields[1].strip()
  if not mocstate:
    raise Exception("mocp --info could not be parsed")
  mocstate.setdefault('State', 'UNKNOWN')  # just in case
  return mocstate


def mocp_play(mocstate):
  if mocstate.get('State') == "PLAY":
    print("mocp is already playing")
  else:
    print("mocp starts playing")
    call("mocp --play".split())


def mocp_stop(mocstate):
  if mocstate.get('State') == "STOP":
    print("mocp isn't playing")
  else:
    print("stopping mocp")
    call("mocp --stop".split())


def mocp_pause(mocstate):
  # using toggle-pause because it's more likely what's expected
  if mocstate.get('State') == "PLAY":
    print("pausing mocp")
    call("mocp --toggle-pause".split())
  elif mocstate['State'] == 'PAUSE':
    print("resuming mocp")
    call("mocp --toggle-pause".split())
  else:
    print("mocp starts playing again")
    call("mocp --play".split())


def mocp_next(mocstate):
  del(mocstate)
  call("mocp --next".split())


def mocp_prev(mocstate):
  del(mocstate)
  call("mocp --prev".split())


def mocp_quit(mocstate):
  del(mocstate)
  print("killing moc")
  call("moc --exit".split())


def mocp_info(mocstate):
  mks = [i for i in mocstate.keys() if i]
  mks.sort()
  blurb = ''
  for i in mks:
    blurb += "\x02{}\x02 {} ".format(i, mocstate[i])
  print(blurb)


def mocp_help(mocstate):
  del(mocstate)
  subcomms = ", ".join(PARAMS.keys())
  print("\x02/mocp\x02 [{}".format(subcomms))


def mocp_np(mocstate):
  if mocstate.get('State') != "PLAY":
    # could be not running; maybe you're using a different music player
    return hexchat.EAT_NONE
  blurb = [mocstate[i] for i in ('Artist', 'SongTitle') if mocstate.get(i)]
  if blurb:
    blurb = " - ".join(blurb)
    hexchat.command("me is listening to \x02{}\x02".format(blurb))
  elif mocstate.get('File'):
    blurb = mocstate['File'][mocstate['File'].rfind('/') + 1:]
    hexchat.command("me is playing \x02{}\x02".format(blurb))
  else:
    print("?? mocp info seems empty ({})".format(repr(mocstate)))


PARAMS = {'help': mocp_help,
          'np': mocp_np,
          'play': mocp_play,
          'stop': mocp_stop,
          'pause': mocp_pause,
          'next': mocp_next,
          'prev': mocp_prev,
          'info': mocp_info,
          'quit': mocp_quit,
          }


def mocp(word, word_eol, userdata):
  " dispatcher for the commands in PARAMS dict() "
  del(word_eol, userdata)
  mocstate = _mocp_state()
  if not mocstate:
    print("MOC is not running?")
    return hexchat.EAT_NONE
  if (len(word)) < 2:
    goto = mocp_info
  else:
    goto = PARAMS.get(word[1], mocp_help)
  goto(mocstate)
  return hexchat.EAT_PLUGIN


def nowplaying(word, word_eol, userdata):
  " dispatcher that plays well with other xchat '/np' plugins "
  del(word, word_eol, userdata)
  mocstate = _mocp_state()
  if mocstate:
    mocp_np(mocstate)
  return hexchat.EAT_NONE  # let another plugin pick it up


print("\x02{}\x02 ({}) {}".format(__module_name__, __module_version__, __module_description__))
call("mocp --server".split(), stderr=DEVNULL)  # starts it if necessary
if __name__ == '__main__':
  # test mode
  hexchat = type('hexchat', (object,), {"EAT_NONE": False, "command": print})
  mocp_info(_mocp_state())
else:
  import hexchat
  print("\x02%s\x02 (%s) %s" % (__module_name__, __module_version__, __module_description__))
  hexchat.hook_command('np', nowplaying, help='same as /mocp np')
  hexchat.hook_command('mocp', mocp, help='/mocp help for what you can do')
  mocp_help(None)
  print("\x02/np\x02 : emotes to current channel what you're listening to")
