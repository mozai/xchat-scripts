""" Xchat module for controlling the Music On Console Player (MOCP)
    program.  Inspired by similar work by kubicz10
"""
from __future__ import print_function
import xchat
import commands

__module_name__  = "MOCP_control"
__module_version__  = "20121202"
__module_description__  = "control music from inside xchat"
__module_author__  =  "Mozai, kubicz10"

def _mocp_status():
  " returns dict() of mocp state info "
  commands.getoutput('mocp --server') # fails silently if unnecessary
  infodump = commands.getoutput("mocp --info")
  mocpinfo = { }
  for line in str(infodump).split("\n"):
    fields = line.split(': ', 2)
    if fields[1].strip():
      mocpinfo[fields[0]] = fields[1].strip()
  if not mocpinfo :
    raise Exception("mocp --info could not be parsed")
  mocpinfo.setdefault('State','UNKNOWN') # just in case
  return mocpinfo

def _mocp_help():
  print("\002/mocp\002 ["+", ".join(PARAMS.keys())+"]")

def _mocp_np():
  mocpinfo = _mocp_status()
  if (mocpinfo['State'] == "STOP"):
    print("mocp isnt running")
  else:
    blurb = [mocpinfo[i] for i in ('Artist', 'Album', 'SongTitle') if mocpinfo.get(i)]
    if blurb :
      blurb = " - ".join(blurb)
      xchat.command("me is listening to \002%s\002" % blurb)
    elif mocpinfo.get('File'):
      blurb = mocpinfo['File'][mocpinfo['File'].rfind('/')+1:]
      xchat.command("me is playing \002%s\002" % blurb)
    else:
      print("?? mocp info seems empty (%s)" % repr(mocpinfo))

def _mocp_play():
  mocpinfo = _mocp_status()
  if (mocpinfo['State'] == "PLAY"):
    print ("mocp is already playing")
  else:
    print("mocp starts playing")
    commands.getoutput("mocp --play")

def _mocp_stop():
  mocpinfo = _mocp_status()
  if (mocpinfo['State'] == "STOP"):
    print ("mocp isn't playing")
  else:
    print("stopping mocp")
    commands.getoutput("mocp --stop")

def _mocp_pause():
  mocpinfo = _mocp_status()
  # using toggle-pause because it's more likely what's expected
  if (mocpinfo['State'] == "PLAY"):
    print("pausing mocp")
    commands.getoutput("mocp --toggle-pause")    
  elif (mocpinfo['State'] == 'PAUSE'):
    print("resuming mocp")
    commands.getoutput("mocp --toggle-pause")
  else:
    print("mocp starts playing again")
    commands.getoutput("mocp --play")

def _mocp_next():
  mocpinfo = _mocp_status()
  if (mocpinfo['State'] == "STOP"):
    print("mocp isn't playing")
  else:
    print("mocp skipping to next track")
    commands.getoutput("mocp --next")

def _mocp_prev():
  mocpinfo = _mocp_status()
  if (mocpinfo['State'] == "STOP"):
    print("mocp isn't playing")
  else:
    print("mocp skipping to previous track")
    commands.getoutput("mocp --prev")

def _mocp_exit():
  print("killing mocp")
  commands.getoutput("mocp --exit")

def _mocp_info():
  mocpinfo = _mocp_status()
  mks = [ i for i in mocpinfo.keys() if i ]
  mks.sort()
  blurb = ''
  for i in mks:
    blurb += "\002%s\002 %s " % (i, mocpinfo[i])
  print(blurb)


PARAMS = { 'help':  _mocp_help,
           'np':    _mocp_np,
           'play':  _mocp_play,
           'stop':  _mocp_stop,
           'pause': _mocp_pause,
           'next':  _mocp_next,
           'prev':  _mocp_prev,
           'info':  _mocp_info,
           'exit':  _mocp_exit,
        }

def mocp(word, word_eol, userdata):
  " dispatcher for the commands in PARAMS dict() "
  if (len(word)) < 2 :
    goto = _mocp_info
  else:
    goto = PARAMS.get(word[1], _mocp_help)
  goto()
  return xchat.EAT_PLUGIN
xchat.hook_command('mocp', mocp , help='/mocp help for what you can do')

def mocp_np(word, word_eol, userdata):
  _mocp_np()
  return xchat.EAT_PLUGIN
xchat.hook_command('np', _mocp_np, help='same as /mocp np')

print("\002%s\002 (%s) %s" % (__module_name__, __module_version__, __module_description__))
commands.getoutput("mocp --server") # starts it if necessary
_mocp_help()
print("\002/np\002 : emotes to current channel what you're listening to")

