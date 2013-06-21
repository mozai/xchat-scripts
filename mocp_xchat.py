""" Xchat module for controlling the Music On Console Player (MOCP)
    program.  Inspired by similar work by kubicz10
"""
from __future__ import print_function
import xchat
import commands

__module_name__  = "MOCP_control"
__module_version__  = "20130620"
__module_description__  = "control music from inside xchat"
__module_author__  =  "Mozai, kubicz10"

def _mocp_state():
  " returns dict() of mocp state info, or None if not running "
  infodump = commands.getoutput("mocp --info")
  if(infodump.find('FATAL_ERROR: The server is not running!') > -1):
    # moc isn't running
    return None
  mocstate = { }
  for line in str(infodump).split("\n"):
    fields = line.split(': ', 2)
    if fields[1].strip():
      mocstate[fields[0]] = fields[1].strip()
  if not mocstate :
    raise Exception("mocp --info could not be parsed")
  mocstate.setdefault('State','UNKNOWN') # just in case
  return mocstate

def mocp_play(mocstate):
  if (mocstate['State'] == "PLAY"):
    print ("mocp is already playing")
  else:
    print("mocp starts playing")
    commands.getoutput("mocp --play")

def mocp_stop(mocstate):
  if (mocstate['State'] == "STOP"):
    print ("mocp isn't playing")
  else:
    print("stopping mocp")
    commands.getoutput("mocp --stop")

def mocp_pause(mocstate):
  # using toggle-pause because it's more likely what's expected
  if (mocstate['State'] == "PLAY"):
    print("pausing mocp")
    commands.getoutput("mocp --toggle-pause")    
  elif (mocstate['State'] == 'PAUSE'):
    print("resuming mocp")
    commands.getoutput("mocp --toggle-pause")
  else:
    print("mocp starts playing again")
    commands.getoutput("mocp --play")

def mocp_next(mocstate):
  del(mocstate)
  commands.getoutput("mocp --next")

def mocp_prev(mocstate):
  del(mocstate)
  commands.getoutput("mocp --prev")

def mocp_quit(mocstate):
  del(mocstate)
  print("killing moc")
  commands.getoutput("moc --exit")

def mocp_info(mocstate):
  mks = [ i for i in mocstate.keys() if i ]
  mks.sort()
  blurb = ''
  for i in mks:
    blurb += "\x02%s\x02 %s " % (i, mocstate[i])
  print(blurb)

def mocp_help(mocstate):
  del(mocstate)
  print("\x02/mocp\x02 ["+", ".join(PARAMS.keys())+"]")
  
def mocp_np(mocstate):
  if (mocstate['State'] == "STOP"):
    print("mocp isnt running")
    return xchat.EAT_PLUGIN
  blurb = [mocstate[i] for i in ('Artist', 'SongTitle') if mocstate.get(i)]
  if blurb :
    blurb = " - ".join(blurb)
    xchat.command("me is listening to \x02%s\x02" % blurb)
  elif mocstate.get('File'):
    blurb = mocstate['File'][mocstate['File'].rfind('/')+1:]
    xchat.command("me is playing \x02%s\x02" % blurb)
  else:
    print("?? mocp info seems empty (%s)" % repr(mocstate)) 

PARAMS = { 'help':  mocp_help,
           'np':    mocp_np,
           'play':  mocp_play,
           'stop':  mocp_stop,
           'pause': mocp_pause,
           'next':  mocp_next,
           'prev':  mocp_prev,
           'info':  mocp_info,
           'quit':  mocp_quit,
        }

def mocp(word, word_eol, userdata):
  " dispatcher for the commands in PARAMS dict() "
  del(word_eol, userdata)
  mocstate = _mocp_state()
  if not mocstate:
    print("MOC is not running?")
    return xchat.EAT_NONE
  if (len(word)) < 2 :
    goto = mocp_info
  else:
    goto = PARAMS.get(word[1], mocp_help)
  goto(mocstate)
  return xchat.EAT_PLUGIN
xchat.hook_command('mocp', mocp , help='/mocp help for what you can do')

def nowplaying(word, word_eol, userdata):
  " dispatcher that plays well with other xchat '/np' plugins "
  del(word, word_eol, userdata)
  mocstate = _mocp_state()
  if mocstate :
    mocp_np(mocstate)
  return xchat.EAT_NONE # let another plugin pick it up
xchat.hook_command('np', nowplaying, help='same as /mocp np')  


print("\x02%s\x02 (%s) %s" % (__module_name__, __module_version__, __module_description__))
mocp_help(None)
print("\x02/np\x02 : emotes to current channel what you're listening to")
commands.getoutput("mocp --server") # starts it if necessary
