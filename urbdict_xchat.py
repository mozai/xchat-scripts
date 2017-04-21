" This is a module for xchat2 / hexchat "
# -- config
# time in seconds between saying stuff out-loud
TIMEOUT = 4
WAITUNTIL = 0

# I forget where I learned this URL. it's valid but undocumented
UD_API = 'http://api.urbandictionary.com/v0/define?page=0&term={}'

# channels to listen for the '`song', '`np' triggers
CHANNELS = ['#farts', '#wetfish', '#test']

# -- init
__module_name__ = "urbandict"
__module_version__ = "20170419"
__module_description__ = "urban dictionary lookups"
__module_author__ = "Mozai <moc.iazom@sesom>"
import hexchat, json, threading, time, urllib.request

# IRC colours as per mIRC:
#   \x0301 black \x0302 blue \x0302,01 blue-on-black \x0f normal
#   \x02 bold \x02 un-bold \x0f normal


def _emit_define(context, term):
  " (thread) fetch urbandict definition, emit it"
  global WAITUNTIL
  try:
    conn = urllib.request.urlopen(UD_API.format(term))
    now = int(time.time())
    i = conn.read().decode('utf-8')
    j = json.loads(i)
    if 'list' not in j:
      # whoasked = ????
      # context.command('msg {} didn\'t find {} in Urban Dictionary.'.format(whoasked, term)
      WAITUNTIL = now + 1
      return None
    defined = j['list'][0]['definition']
    if context:
      context.command('me \x02checks urbdict:\x02 "{}"'.format(defined))
      WAITUNTIL = now + TIMEOUT
    else:
      print('\x02UD says:\x02 "{}"'.format(defined))
      WAITUNTIL = now + TIMEOUT
    return hexchat.EAT_PLUGIN
  except Exception as err:
    print(repr(err))
    return None


def ud_listening(word, word_eol, userdata):
  del(userdata)  # shut up pylint
  global WAITUNTIL
  now = int(time.time())
  if (now <= WAITUNTIL):
    return None
  context = hexchat.get_context()
  chan = context.get_info('channel')
  if ((len(CHANNELS) > 0) and (chan not in CHANNELS)):
    return None
  useful = word[1].split(None, 1)
  # "!ud argle bargle" -> ["!ud", "argle bargle"]
  # "!ud" -> ["!ud"]
  if len(useful) == 2 and useful[0] in ('!ud', '`ud'):
    drone = threading.Thread(target=_emit_define, args=(context, useful[1]))
    drone.daemon = True
    drone.start()
  return hexchat.EAT_PLUGIN


def ud_command(word, word_eol, userdata):
  del(userdata)  # shut up pylint
  params = word_eol[1]
  if not params:
    print("{} term : go fetch the first UrbanDictionary definition of term".format(word[0]))
  else:
    _emit_define(None, params)

hexchat.hook_print('Channel Message', ud_listening)
# hexchat.hook_server('PRIVMSG', ud_listening)
hexchat.hook_print('Your Message', ud_listening)
hexchat.hook_command('ud', ud_command, help='go fetch the furst UrbanDictionary definition of param')
print("urbdict loaded (!ud term, `ud term, /ud term)")
