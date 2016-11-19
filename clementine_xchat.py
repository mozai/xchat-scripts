" Hexchat module for controlling the Clementine media player "
# Python 3.x ; don't need str.encode('utf8') anymore
from __future__ import print_function
import hexchat
import dbus

__module_name__ = "Clementine"
__module_version__ = "20161114"
__module_description__ = "control music from inside hexchat"
__module_author__ = "Mozai"


# MPRIS GetStatus() = [ [Playing, Paused, Stopped],
#                       [Sequential, Shuffle],
#                       [Play Song Once, Repeat Song],
#                       [Play List Once, Repeat List]
#                     ]

def _clementine_iface():
  try:
    thebus = dbus.SessionBus()
    # I tried leaving BUS as a module global, but it stopped working
    # do dbus sessions time out?
    playr = thebus.get_object('org.mpris.clementine', '/Player')
    iface = dbus.Interface(playr, dbus_interface='org.freedesktop.MediaPlayer')
    return iface
  except dbus.exceptions.DBusException:
    # "org.freedesktop.DBus.Error.ServiceUnknown" Clementine isn't running
    return None


def clem_np(iface):
  songdata = iface.GetMetadata()
  tna = [songdata[i] for i in ('title', 'artist') if songdata.get(i)]
  loc = songdata.get('location')
  if tna:
    tna = "\x02 by \x02".join(tna)
    tna = "\x02" + tna[:255] + "\x02"  # sanity check
    hexchat.command("me is listening to {}".format(tna))
  elif loc:
    if loc.startswith('file:'):
      # I want not the full path
      loc = loc[loc.rfind('/', 0, loc.rfind('/')) + 1:]
      loc = loc[:255]  # sanity check
    hexchat.command("me is listening to \x02%s\x02" % loc)
  else:
    print("clementine isn't playing")
  return hexchat.EAT_NONE


def clem_play(iface):
  stat = iface.GetStatus()[0]
  if stat == 0:
    print("clementine is already playing")
  else:
    print("clementine starts playing")
    iface.Play()


def clem_stop(iface):
  stat = iface.GetStatus()[0]
  if stat == 2:
    print("clementine is already stopped")
  else:
    print("clementine stops")
    iface.Stop()


def clem_pause(iface):
  iface.Pause()


def clem_next(iface):
  iface.Next()


def clem_prev(iface):
  iface.Prev()


def clem_quit(iface):
  del(iface)  # shut up pylint
  print("killing clementine")
  thebus = dbus.SessionBus()
  thebus.get_object('org.mpris.clementine', '/').Quit()


def clem_info(iface):
  mdata = iface.GetMetadata()
  if mdata:
    blurb = ''
    for i in sorted(mdata.keys()):
      blurb += "\x02{}\x02 {} ".format(i, mdata[i])
    print(blurb)
  else:
    print("clementine not playing?")


def clem_help(iface):
  del(iface)  # shut up pylint
  print('\x02/clem\x02 [ ' + ', '.join(PARAMS.keys()) + ' ]')
  print("\x02/np\x02 : emotes to current channel what you're listening to")

PARAMS = {
  'np':    clem_np,
  'play':  clem_play,
  'stop':  clem_stop,
  'pause': clem_pause,
  'next':  clem_next,
  'prev':  clem_prev,
  'info':  clem_info,
  'quit':  clem_quit,
  'help':  clem_help,
}


def clem(word, word_eol, userdata):
  " dispatcher for the commands in PARAMS dict() "
  del(word_eol, userdata)  # shut up, pylint
  iface = _clementine_iface()
  if not iface:
    # Clementine not running; maybe some other media player
    print("clementine is not running?")
    return hexchat.EAT_PLUGIN
  if (len(word)) < 2:
    goto = clem_info
  else:
    goto = PARAMS.get(word[1], clem_help)
  goto(iface)
  return hexchat.EAT_PLUGIN
hexchat.hook_command('clem', clem, help='/clem help for what you can do')


def nowplaying(word, word_eol, userdata):
  " dispatcher that plays well with other hexchat '/np' plugins "
  iface = _clementine_iface()
  del(word, word_eol, userdata)
  if iface:
    clem_np(iface)
  return hexchat.EAT_NONE  # let another plugin pick it up
hexchat.hook_command('np', nowplaying, help='same as /clem np')

print("\x02%s\x02 (%s) %s" % (__module_name__, __module_version__, __module_description__))
clem_help(None)

