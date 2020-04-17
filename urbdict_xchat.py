" This is a module for xchat2 / hexchat "
# problem: any http request could take up to 30 seconds
#   but we can't block all of hexchat to wait
#   AND 'threading' module will sometimes crash ALL of hexchat
#   (may be a persistent bug in Gtk_object)
#   when trying to modify gtk objects from a child thread
#   "don't update gtk ui directly from any thread"
# TODO: hexchat uses Python 3.5, try using 'asyncio' module instead?
import hexchat
import json
import re
from threading import Thread
import time
import urllib.request

# -- config
# time in seconds between saying stuff out-loud
TIMEOUT = 5

# channels to listen for the '`ud' trigger
LISTEN_TO = '#farts #wetfish #test'

# I forget where I learned this URL. it's valid but undocumented
UD_API = 'http://api.urbandictionary.com/v0/define?page=0&term={}'


# -- init
__module_name__ = "urbandict"
__module_version__ = "20170701"
__module_description__ = "urban dictionary lookups"
__module_author__ = "Mozai <moc.iazom@sesom>"


# IRC colours as per mIRC:
#   \x0301 black \x0302 blue \x0302,01 blue-on-black \x0f normal
#   \x02 bold \x02 un-bold \x0f normal

# my god this is ugly; I'm depending on side-effects
#   the alternative is to use context.command() from inside a child thread
#   which will crash all of hexchat :(

CHANNELS = {i: {'req': False, 'resp': False, 'wait': 0} for i in LISTEN_TO.split()}

def _drone(userdata):
  " given an entry in dict CHANNELS, populates the 'resp' key "
  if userdata.get('req') is None:
    return None
  if userdata.get('resp') is not None:
    return userdata['resp']
  answer = None
  try:
    conn = urllib.request.urlopen(UD_API.format(param))
    i = conn.read().decode('utf-8')
    j = json.loads(i)
    if j.get('list'):
      answer = j['list'][0]['definition']
      answer = re.sub(r'\s+', ' ', defined)
      if len(answer) > 200:
        answer = answer[:195] + ' ...'
  except Exception as err:
    pass  # TODO: how to report error without talking to GTK ui elements?
  finally:
    userdata['req'] = None
    userdata['resp'] = answer
  return answer


def _emit_definition(userdata):
  " (thread) fetch urbandict definition, emit it"
  # if using .hook_timer(), returning 'True' will re-hook_timer() this
  now = int(time.time())
  if userdata['conch']:
    # we're already running
    return False
  if now <= userdata['wait']:
    # TODO: maybe tell user to wait
    return False
  context = userdata.get('context')
  param = userdata.get('param')
  try:
    userdata['conch'] = True
    conn = urllib.request.urlopen(UD_API.format(param))
    i = conn.read().decode('utf-8')
    j = json.loads(i)
    defined = ''
    if j.get('list'):
      defined = j['list'][0]['definition']
      defined = re.sub(r'\s+', ' ', defined)
      if len(defined) > 200:
        defined = defined[:195] + ' ...'
  except Exception as err:
    userdata['conch'] = False
    raise
  if context:
    if defined:
      context.command('me \x02urbdict:\x02 "{}"'.format(defined))
      userdata['wait'] = now + TIMEOUT
    else:
      context.command('me \x02urbdict:\x02 "{}" not found'.format(param))
      userdata['wait'] = now + 1
  else:
    if defined:
      print('\x02UD says:\x02 "{}"'.format(defined))
    else:
      print('\x02UD:\x02 term "{}" not found'.format(param))
  userdata['context'] = None
  userdata['param'] = None
  userdata['conch'] = False
  return False  # don't keep repeating the .hook_timeout()


def ud_listening(word, word_eol, userdata):
  del(userdata)  # shut up pylint
  context = hexchat.get_context()
  chan = context.get_info('channel')
  userdata = CHANNELS.get(chan)
  if userdata is None:
    return None
  useful = word[1].split(None, 1)
  # "!ud argle bargle" -> ["!ud", "argle bargle"]
  # "!ud" -> ["!ud"]
  if len(useful) == 2 and useful[0] in ('!ud', '`ud'):
    userdata['context'] = context
    userdata['param'] = useful[1]
    # tried using .hook_timer() because threading is causing crashes
    #userdata['hook'] = hexchat.hook_timer(10, _emit_definition, userdata)
    drone = Thread(target=_emit_nowplaying, args=(userdata,))
    drone.daemon = True
    drone.start()

  return hexchat.EAT_PLUGIN


def ud_command(word, word_eol, userdata):
  del(userdata)  # shut up pylint
  term = word_eol[1]
  if not term:
    print("{} term : go fetch the first UrbanDictionary definition of term".format(word[0]))
  else:
    userdata = {'conch': False, 'context': None, 'param': term, 'wait': 0}
    userdata['hook'] = hexchat.hook_timer(100, _emit_definition, userdata)


hexchat.hook_print('Channel Message', ud_listening)
# hexchat.hook_server('PRIVMSG', ud_listening)
hexchat.hook_print('Your Message', ud_listening)
hexchat.hook_command('ud', ud_command, help='go fetch the furst UrbanDictionary definition of param')
print("urbdict loaded (!ud term, `ud term, /ud term)")
