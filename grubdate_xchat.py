"""
  this is a python script for use with hexchat v2.x. w/ python 3

  grubdate.ini will look like this:
    [DEFAULT]
    refresh=300
    throttle=300

    [mspa]
    name=MSPA
    url=http://mspaintadventures.com/rss/rss.xml
    command=grubdate
    listento=#test,#farts
    listenfor=.mspa
    listenmsg={name} hasn't had a new page since {when}
    announceto=#farts
    announcemsg=Homestuck upd8!

  The DEFAULT section is fallback for items not mentioned in sections.
  'name': human friendly name (required)
  'url': site to check (required)
  'refresh': time between checks (default: 300 seconds, min 120 seconds)
  'throttle': time between answering listenfor triggers (default: 60 seconds)
  'command': the /slash command you can type to get an answer
  'listento': channels to listen for listenfor commands
  'listenfor': if someone says this on a line by itself, respond with info
  'listenmsg': how to reply (default: '{name} updated \x02{when}\x02'
  'announceto': if the url updates, announce to these channels
  'announcemsg': what to say on update (default: '* {name} updated *')
"""
# Python 3.x
# rewrote this to use hook_timer() instead of multithreading
#  because multithreating makes hexchat 2.12 hang and crash
import hexchat
from configparser import ConfigParser
from email.utils import parsedate_tz, mktime_tz
import re
import time
import os
import urllib.request
__module_name__ = "grubdate"  # it's a Homestuck joke
__module_version__ = "20170504"
__module_description__ = "website update check"
__module_author__ = "Mozai <moc.iazom@sesom>"
DEBUG = True

# -- config, stuff the user will want to mess with
# because (he)xchat, I'll have to search many directories to find it
INI_FILE = 'grubdate.ini'

# TODO: don't speak if this nick (another bot) is in the channel
# AFRAID_OF = ('jade_harley',)

# how often the heartbeat pumps, to check websites, in miliseconds
HB_TIME = 8 * 60 * 1000  # eight minutes

# -- init


def _quack(msg):
  " debug messages "
  if DEBUG:
    print("({}: {})".format(__module_name__, msg))


def dump_state(word, word_eol, userdata):
  " used for debugging "
  global SITES
  del(word_eol, userdata)  # shut up, pylint
  print("dumping {} state data".format(__module_name__))
  for site in SITES:
    print("{}: {} ".format(site, repr(SITES[site])))
  print("---")


def _secs_to_pretty(ticks=0):
  " given ticks as a duration in seconds, in human-friendly units "
  day, remain = divmod(ticks, (24 * 60 * 60))
  hour, remain = divmod(remain, (60 * 60))
  minute, second = divmod(remain, 60)
  if day > 0:
    return "%dd %dh" % (day, hour)
  elif hour > 0:
    return "%dh %dm" % (hour, minute)
  elif minute > 0:
    return "%dm %ds" % (minute, second)
  else:
    return "less than a minute"


def nowtime():
  return int(time.mktime(time.gmtime()))


# read the grubdate.ini file
def ini_load(ini_file):
  " given filename.ini, sets global SITES dict "
  global SITES
  iniparser = ConfigParser(allow_no_value=True)
  # have to search for where the ini could be
  found = None
  configdir = hexchat.get_info('configdir')
  possible_dirs = (configdir + os.sep + 'addons', configdir, '.')
  for i in possible_dirs:
    found = iniparser.read(i + os.sep + ini_file)
    if found:
      ini_file = found
      break
  if not found:
    raise Exception("Could not find config file {}".ini_file)
  # so I tried using the ConfigParser object to hold state but
  # turns out it will ONLY allow assigning strings, not integers
  SITES = {}
  now = nowtime()
  for i in iniparser.keys():
    if i == 'DEFAULT':
      continue
    SITES[i] = {}
    site = SITES[i]
    for j in iniparser[i].keys():
      site[j] = iniparser[i].get(j)
    if not site.get('url'):
      print("{}: missing 'url' in [{}]".format(ini_file, i))
      site['url'] = None
      site['refresh'] = 86400 * 365  # something nonsensically long
    site.setdefault('name', i)
    site.setdefault('listento', '')
    site['listento'] = site['listento'].split(',')
    site.setdefault('announcemsg', '\x02* {name} updated!\x02')
    site.setdefault('listenmsg', '{name} updated \x02{when}\x02 ago')
    site.setdefault('throttle', 60)
    site.setdefault('refresh', 300)
    site['lastanno'] = now
    site['atime'] = 0
    site['mtime'] = 0
  return SITES


def _announce_update(site):
  " bleat to the appropriate channels "
  now = nowtime()
  if site['mtime'] == 0:
    # last-modified time is still empty? how'd we get here?
    return None
  if (site['lastanno'] + site['throttle']) > now:
    # too soon since the last announcement, just stay mum
    return None
  if site.get('announceto'):
    message = site.get('announcemsg')
    message = message.replace('{name}', site['name'])
    message = message.replace('{when}', _secs_to_pretty(now - site['mtime']))
    targets = [i for i in site['announceto'] if i.startswith('#')]
    for target in targets:
      # can't use hexchat.get_context(None, channname)
      # because that returns only the random first matching context
      for channel in hexchat.get_list('channels'):
        if channel.channel == target:
          channel.context.command("say " + message)
    targets = [i for i in site['announceto'] if not i.startswith('#')]
    for target in targets:
      # TODO: find user among many servers
      # hexchat.command("msg {} {}".format(target, message))
      print("NotImplemented msg % % .format({}, {})".format(target, message))
  site['lastanno'] = now


def _update_site(site):
  # skips update if now < site['atime'] + site.get('refresh', 300))
  now = nowtime()
  if now <= (site['atime'] + site['refresh']):
    return None
  if not site.get('url'):
    site['atime'] = now
    return None
  with urllib.request.urlopen(site['url'], timeout=2) as res:
    site.pop('error', None)  # del(site['error']) without throwing KeyError
    site['atime'] = now
    if res.status >= 300:
      site['error'] = "http {} {}".format(res.status, res.reason)
      print("\002ERROR: grubdate could not fetch {} {}: \"{}\" ".format(site['name'], site['url'], site['error']))
      return None
    webpage = str(res.read())
    # expects to see RSS XML or Atom XML
    # first {pubdate,updated} tag should be most recent
    new_mtime = None
    matchobj = re.search(r'<pubdate>([^<]*)</pubdate>', webpage, re.S | re.I)
    if matchobj:
      last_modified = matchobj.group(1)
      new_mtime = mktime_tz(parsedate_tz(last_modified))
    if not new_mtime:
      matchobj = re.search(r'<updated>([^<]*)</updated>', webpage, re.S | re.I)
      if matchobj:
        last_modified = matchobj.group(1)
        new_mtime = mktime_tz(parsedate_tz(last_modified))
    if not new_mtime:
      if res.getheader('Last-Modified'):
        last_modified = res.getheader('Last-Modified')
        new_mtime = mktime_tz(parsedate_tz(last_modified))
  if new_mtime:
    if new_mtime > site['mtime']:
      site['mtime'] = new_mtime
      return site['mtime']
  else:
    site['error'] = "did not find pubdate/updated/last-modified in response"
  return None


def _update_sites(userdata):
  global SITES
  del(userdata)  # shut up, pylint
  for i in SITES:
    if nowtime() <= (SITES[i]['atime'] + SITES[i]['refresh']):
      return None
    retval = _update_site(SITES[i])
    # how do I avoid the above from blocking the loop
    # without using threads? beacuse spawning threads messes up hexchat
    if retval is not None:
      _announce_update(SITES[i])
  return True  # keep hook_timer(n, f) going


def _update_sites_once(userdata):
  # gimmick to jump the first heartbeat
  _update_sites(userdata)
  return False  # end hook_timer(n, r) immediately after


def emit_mtime(context, site):
  if site['mtime'] == 0:
    return None
  ago = _secs_to_pretty(nowtime() - site['mtime'])
  if context is None:
    print("{} updated \002{}\002 ago".format(site['name'], ago))
  elif isinstance(context, str):
    hexchat.command("msg {} {} updated \002{}\002 ago".format(context, site['name'], ago))
  else:
    context.command("say {} updated \002{}\002 ago".format(site['name'], ago))
    site['lastanno'] = nowtime()


def checkCommand(word, word_eol, userdata):
  """ respond to "/(SITES[]['command'])" messages
      prints to local client window
  """
  del(word_eol, userdata)  # shut up, pylint
  for i in SITES:
    if 'command' not in SITES[i]:
      continue
    if word[0] == SITES[i]['command']:
      emit_mtime(None, SITES[i])
      return hexchat.EAT_PLUGIN
    elif word[0] == SITES[i]['command'] + '_emote':
      emit_mtime(hexchat.get_context(), SITES[i])
      return hexchat.EAT_PLUGIN


def eat_privmsg(word, word_eol, userdata):
  context = hexchat.get_context()
  who = word[0][1:word[0].find('!')]
  # where = word[2]
  chan = context.get_info('channel')
  what = word_eol[3][1:]
  words = what.strip().split()
  if not words:
    # degenerate case of "nick PRIVMSG #channel :\r\n"
    return None
  now = nowtime()
  site = None
  for i in SITES:
    if SITES[i].get('listenfor') == words[0]:
      if SITES[i].get('listento'):
        if chan in SITES[i]['listento']:
          site = SITES[i]
      else:
        # assume all channels if none are mentioned
        site = SITES[i]
  if site is None:
    return None
  if (site['lastanno'] + site['throttle']) > now:
    # send message to just this person, and don't reset the lastasked time
    context = who
  # elif AFRAID_OF:
  #   nicks = [i.nick.lower() for i in context.get_list('users')]
  #   afraid = [i for i in nicks if i in AFRAID_OF]
  #   if afraid:
  #     send message to just this person, because I'm scared
  #     context = who
  else:
    site['lastasked'] = now
  emit_mtime(context, site)
  return hexchat.EAT_PLUGIN


# -- main
print("\002Loaded {} v{}\002".format(__module_name__, __module_version__))
ini_load(INI_FILE)

# the automatic thing
# does the timer automatically stop when this module is unloaded?
TIMER1 = hexchat.hook_timer(HB_TIME, _update_sites)
TIMER2 = hexchat.hook_timer(1, _update_sites_once)

# the /commands
CLIST = ''
for SITE in SITES:
  if 'command' in SITES[SITE]:
    hexchat.hook_command(SITES[SITE]['command'], checkCommand, help='show you %s age' % SITES[SITE]['name'])
    CLIST += '/' + SITES[SITE]['command'] + ' '
    hexchat.hook_command(SITES[SITE]['command'] + '_emote', checkCommand, help='announces %s age' % SITES[SITE]['name'])
    CLIST += '/' + SITES[SITE]['command'] + '_emote '
print("\002commands:\002", CLIST)
hexchat.hook_command('grubdate_dump', dump_state, help='(debug) dump SITES dict for grubdate')
print("\002debug commands:\002 /grubdate_dump")

# the triggers
CLIST = ''
for SITE in SITES:
  if 'listenfor' in SITES[SITE]:
    CLIST += SITES[SITE]['listenfor'] + ' '
print("\002triggers:\002", CLIST)
hexchat.hook_server("PRIVMSG", eat_privmsg)


# cleanup, don't wait for GC
del(CLIST, SITE)
