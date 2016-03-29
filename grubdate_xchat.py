"""
  this is a python script for use with xchat v2.x.

  INSTALL: put into ~/.xchat2/ and it should load on restart
    or you can type '/py load grubdate-xchat.py' into xchat
    it expects a 'grubdate.ini' file in the same directory.

  grubdate.ini will look like this:
    [DEFAULT]
    checkpause=120
    askpause=600

    [mspa]
    name=MSPA rss feed
    url=http://mspaintadventures.com/rss/rss.xml
    command=grubdate
    flair= according to my watch.
    trigger=.update
    channels=#farts,#test

  The DEFAULT section is fallback for items not mentioned in others
  Each other section defines a website and related commands for checking
    to see if the website updated.
  The items 'name', 'host' and 'path' are required, and should be obvious.
  'command' becomes "/grubdate" and "/grubdate_emote"
  'trigger' becomes listening for ".update" in channels
  'channels' is a ,-seperated list of channels to listen in (none means all)
  'flair' is added on the end of "%name updated %time ago%flair"
  'checkpause' is how many seconds to cache checking the website
  'askpause' is how many seconds until a trigger will speak out loud again

  AUTHOR: Moses Moore <moc.iazom@sesom>

  If you care, pretend this was released under the GPL license
  http://www.gnu.org/copyleft/gpl.html

"""
# -- config, stuff the user will want to mess with
INI_FILE = '.xchat2/grubdate.ini'

# for irc://rizon.net/#farts
# don't speak if this nick is in the channel
AFRAID_OF = ('jade_harley',)
AFRAID_OF = [str.lower(A) for A in AFRAID_OF]

# -- init, stuff we do only once
import xchat
# import commands
import ConfigParser
import dateutil.parser
import re
import requests
import rfc822
import threading
import time

__module_name__ = "grubdate"  # it's a Homestuck joke
__module_version__ = "20160328"
__module_description__ = "website update check"
__module_author__ = "Mozai <moc.iazom@sesom>"

# read the grubdate.ini file
CONF = ConfigParser.ConfigParser(allow_no_value=True)
INI_LOADED = CONF.read(INI_FILE)
if len(INI_LOADED) < 1:
  INI_LOADED = CONF.read('./grubdate.ini')
  print "...attempting to load ./grubdate.ini instead."
if len(INI_LOADED) > 0:
  SITES = dict()
  for SITE in CONF.sections():
    SITES[SITE] = dict()
    for item in CONF.items(SITE):
      SITES[SITE][item[0]] = item[1]
    SITES[SITE]['askpause'] = int(SITES[SITE]['askpause'])
    SITES[SITE]['checkpause'] = int(SITES[SITE]['checkpause'])
    SITES[SITE]['lastasked'] = 0
    SITES[SITE]['lastchecked'] = 0
    SITES[SITE]['lastmodified'] = 0
    if 'channels' in SITES[SITE]:
      SITES[SITE]['channels'] = SITES[SITE]['channels'].split(',')
else:
  raise Exception('no config loaded; missing %s ?' % INI_FILE)
del(CONF, INI_FILE, INI_LOADED)  # don't wait for GC that won't happen


def _secsToPretty(ticks=0):
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


def _getLastModified(site):
  """ given an entry in the SITES[] global dict, returns age in seconds
  if request is less than SITES[site]['checkpause'] ago, returns cached answer
  """
  now = time.mktime(time.gmtime())
  if now >= (site['lastchecked'] + site['checkpause']):
    req = requests.request('HEAD', site['url'], timeout=3)
    if req.status_code >= 300:
      print "QUACK %s responded with http %d %s" % (site['url'], req.status_code, req.reason)
      return None
    if 'Last-Modified' in req.headers:
      last_modified = req.headers['Last-Modified']
      timetuple = rfc822.parsedate(last_modified)
      site['lastmodified'] = time.mktime(timetuple)
      site['lastchecked'] = now
    else:
      # dirty methods ahoy
      # expects to see RSS XML or Atom XML
      req = requests.request('GET', site['url'], timeout=3)
      now = time.mktime(time.gmtime())
      matchobj1 = re.search(r'<pubdate>([^<]*)</pubdate>', req.text, re.S | re.I)
      matchobj2 = re.search(r'<updated>([^<]*)</updated>', req.text, re.S | re.I)
      if matchobj1:
        last_modified = matchobj1.group(1)
        last_modified = dateutil.parser.parse(last_modified)
        site['lastmodified'] = time.mktime(last_modified.timetuple())
      elif matchobj2:
        last_modified = matchobj1.group(1)
        last_modified = dateutil.parser.parse(last_modified)
        site['lastmodified'] = time.mktime(last_modified.timetuple())
      else:
        print "QUACK didn't find date in %s" % (site['url'])
        return None
  return site['lastmodified']


def _emit_lastmodified(context, site):
  " (thread) get mtime of a site, respond into xchat context "
  mtime = _getLastModified(site)
  if mtime:
    flair = site.get('flair', '')
    now = time.mktime(time.gmtime())
    if isinstance(context, str):
      xchat.command("msg {} {} updated \002{}\002 ago{}".format(context, site['name'], _secsToPretty(now - mtime), flair))
    elif context is not None:
      context.command("say {} updated \002{}\002 ago{}".format(site['name'], _secsToPretty(now - mtime), flair))
    else:
      print "%s updated \002%s\002 ago%s" % (SITES[site]['name'], _secsToPretty(now - mtime), flair)
  else:
    if isinstance(context, str):
      xchat.command("msg {} {} couldn't get a decent update; try again later?".format(context, site['name']))
    elif context is not None:
      context.command("say {} couldn't get a decent update; try again later?".format(site['name']))
    else:
      print "{} couldn't get a decent update; try again later?".format(site['name'])


def checkCommand(word, word_eol, userdata):
  """ respond to "/(SITES[]['command'])" messages
      prints to local client window
  """
  del(word_eol, userdata)  # shut up, pylint
  site = None
  context = None
  for i in SITES:
    if ('command' in SITES[i]) and (word[0] == SITES[i]['command']):
      site = i
  if site is None:
    for i in SITES:
      if ('command' in SITES[i]) and (word[0] == SITES[i]['command'] + '_emote'):
        site = i
        context = xchat.get_context()
  if site is None:
    return None
  else:
    _emit_lastmodified(context, site)
    return xchat.EAT_PLUGIN


def _inany(needle, haystack):
  # because 'needle' in 'haystackneedle' returns True
  if haystack is None:
    return False
  if isinstance(haystack, (list, tuple, dict)):
    return needle in haystack
  elif isinstance(haystack, (str, unicode)):
    return needle == haystack
  else:
    raise TypeError('unknown haystack type:', type(haystack))


def checkPrint(word, word_eol, userdata):
  """ if it matches SITES[]['trigger'],
      if it's been SITES[]['askpause'] since last, respond with an emote.
      if it's less than that since last, respond with a privmsg.
  """
  del(word_eol, userdata)  # shut up, pylint
  context = xchat.get_context()
  chan = context.get_info('channel')
  who = word[0]
  cmd = word[1].split()[0]
  now = int(time.time())
  if cmd == '':
    return None
  site = None
  for site_key in SITES:
    if SITES[site_key].get('trigger') == cmd:
      if 'channels' in SITES[site_key]:
        if _inany(chan, SITES[site_key]['channels']):
          site = SITES[site_key]
      else:
        # else no channels are mentioned
        site = SITES[site_key]
  if not site:
    return None
  nicks = [i.nick.lower() for i in context.get_list('users')]
  afraid_of = [i for i in nicks if i in AFRAID_OF]
  if afraid_of:
    print "(staying quiet because I'm scared of {})".format(afraid_of)
    return None
  pauseleft = site['lastasked'] + site['askpause'] - now
  if pauseleft > 0:
    # send message to just this person, and don't reset the lastasked time
    context = who
  else:
    site['lastasked'] = now
  drone = threading.Thread(target=_emit_lastmodified, args=(context, site))
  drone.daemon = True
  drone.start()
  return xchat.EAT_PLUGIN


# -- main
print "\002Loaded %s v%s\002" % (__module_name__, __module_version__)
CLIST = ''
for SITE in SITES:
  if 'command' in SITES[SITE]:
    xchat.hook_command(SITES[SITE]['command'], checkCommand, help='show you %s age' % SITES[SITE]['name'])
    CLIST += '/' + SITES[SITE]['command'] + ' '
    xchat.hook_command(SITES[SITE]['command'] + '_emote', checkCommand, help='announces %s age' % SITES[SITE]['name'])
    CLIST += '/' + SITES[SITE]['command'] + '_emote '
print "\002commands:\002", CLIST

CLIST = ''
xchat.hook_print('Channel Message', checkPrint)
xchat.hook_print('Your Message', checkPrint)
for SITE in SITES:
  if 'trigger' in SITES[SITE]:
    CLIST += SITES[SITE]['trigger'] + ' '
print "\002triggers:\002", CLIST

del(CLIST, SITE)  # don't wait for GC that will never happen
