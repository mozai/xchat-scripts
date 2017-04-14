" Hexchat module for controlling the Clementine media player "
# Python 3.x ; don't need str.encode('utf8') anymore
# 2017 April: Clementine dropped support for MPRIS1
#    now it's way more complicated
# MPRIS1:
#   qdbus org.mpris.clementine /Player org.freedesktop.MediaPlayer.GetMetadata
# MPRIS2:
#   qdbus org.mpris.MediaPlayer2.clementine /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get org.mpris.MediaPlayer2.Player Metadata
#   ... and the dict we get has 'xesam:' prefixed to most but not every key???
# TODO: why does clementine lock-up if this module is reloaded or unloaded?
from __future__ import print_function
import hexchat
import dbus

__module_name__ = "Clementine"
__module_version__ = "20170414"
__module_description__ = "control music from inside hexchat"
__module_author__ = "Mozai"


def _clementine_obj():
  try:
    i = dbus.SessionBus()
    # I know it sucks to make a new session each time, but
    #   they don't persist.  Maybe they time-out?
    return i.get_object('org.mpris.MediaPlayer2.clementine', '/org/mpris/MediaPlayer2')
  except dbus.exceptions.DBusException as err:
    print("is clementine running? ({})".format(err))
    return None


def _clem_status():
  clem = _clementine_obj()
  if clem:
    iface = dbus.Interface(clem, dbus_interface='org.freedesktop.DBus.Properties')
    return iface.GetAll('org.mpris.MediaPlayer2.Player')


def _clem_player():
  clem = _clementine_obj()
  if clem:
    return dbus.Interface(clem, dbus_interface='org.mpris.MediaPlayer2.Player')


def clem_np():
  status = _clem_status()
  if not status:
    return hexchat.EAT_NONE
  if status['PlaybackStatus'] != 'Playing':
    print("clementine isn't playing")
    return
  metadata = status['Metadata']
  title = str(metadata.get('xesam:title', metadata.get('title')))
  if 'xesam:artist' in metadata:
    artist = str(metadata.get('xesam:artist')[0])
  elif 'artist' in metadata:
    artist = str(metadata.get('artist'))
  loc = str(metadata.get('xesam:url', metadata.get('url', metadata.get('location'))))
  if title or artist:
    title = title or "Unknown"
    artist = artist or "Unknown"
    hexchat.command("me is listening to \x02{}\x02 by \x02{}\x02".format(title[:63], artist[:63]))
  elif loc:
    if loc.startswith('file:'):
      # I want not the full path
      loc = loc[loc.rfind('/', 0, loc.rfind('/')) + 1:]
      loc = loc[:255]  # sanity check
    hexchat.command("me is listening to \x02{}\x02".format(loc))
  else:
    print("don't know what clemtine is playing (no title, artist nor url?)")


def clem_play(iface):
  status = _clem_status()
  if status:
    if status['PlayStatus'] == 'Playing':
      print("clementine is already playing")
    else:
      _clem_player().Play()


def clem_stop(iface):
  status = _clem_status()
  if status:
    if status['PlayStatus'] == 'Stopped':
      print("clementine is already stopped")
    else:
      _clem_player().Stop()


def clem_pause(iface):
  clem = _clem_player()
  if clem:
    clem.PlayPause()  # toggle


def clem_next(iface):
  clem = _clem_player()
  if clem:
    clem.Next()


def clem_prev(iface):
  clem = _clem_player()
  if clem:
    clem.Previous()


def clem_quit():
  clem = _clem_player()
  if clem:
    clem.Quit()


def clem_info():
  status = _clem_status()
  if status:
    for i in sorted([str(j) for j in status.keys()]):
      if i != 'Metadata':
        print("\x02{}\x02: {} ".format(i, status[i]))
      else:
        print("\x02Metadata:\x02:")
        for i2 in sorted([str(j2) for j2 in status['Metadata'].keys()]):
          print("\x02  {}\x02: {} ".format(i2, status['Metadata'][i2]))
  else:
    print("clementine not playing?")


def clem_help():
  print('\x02/clem\x02 [ ' + ', '.join(SUBCOMMANDS.keys()) + ' ]')
  print("\x02/np\x02 : emotes to current channel what you're listening to")


SUBCOMMANDS = {
  'np': clem_np,
  'play': clem_play,
  'stop': clem_stop,
  'pause': clem_pause,
  'next': clem_next,
  'prev': clem_prev,
  'info': clem_info,
  'quit': clem_quit,
  'help': clem_help,
}


def clem(word, word_eol, userdata):
  " dispatcher for the commands in PARAMS dict() "
  del(word_eol, userdata)  # shut up, pylint
  status = _clem_status()
  if not status:
    print("clementine is not running?")
    return hexchat.EAT_PLUGIN
  if (len(word) > 1) :
    goto = SUBCOMMANDS.get(word[1], clem_help)
  else:
    goto = clem_help
  goto()


def nowplaying(word, word_eol, userdata):
  " dispatcher that plays well with other hexchat '/np' plugins "
  del(word, word_eol, userdata)
  clem_np()
  return hexchat.EAT_NONE  # let another plugin pick it up


print("\x02%s\x02 (%s) %s" % (__module_name__, __module_version__, __module_description__))
hexchat.hook_command('clem', clem, help='/clem help for what you can do')
hexchat.hook_command('np', nowplaying, help='same as /clem np')
clem_help()
