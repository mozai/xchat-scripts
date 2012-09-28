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
    host=mspaintadventures.com
    path=/rss/rss.xml
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
# blaaaargh, tried to make this conform to PEP-8 coding standards
# but I refuse to give up mixedCase function names
# and I refuse to use four-space indents, yuck.

# -- config, stuff the user will want to mess with
INI_FILE = '.xchat2/grubdate.ini'


# -- init, stuff we do only once
import xchat
# import commands
import httplib, time, rfc822, ConfigParser

__module_name__  = "grubdate"  # it's a Homestuck joke
__module_version__  = "20120910"
__module_description__  = "website update check"
__module_author__  =  "Mozai <moc.iazom@sesom>"

# read the grubdate.ini file
CONF = ConfigParser.ConfigParser(allow_no_value=True)
INI_LOADED = CONF.read(INI_FILE)
if len(INI_LOADED) > 0 :
  SITES = dict()
  for SITE in CONF.sections():
    SITES[SITE] = dict()
    for item in CONF.items(SITE):
      SITES[SITE][item[0]]  =  item[1]
    SITES[SITE]['askpause']     = int(SITES[SITE]['askpause'])
    SITES[SITE]['checkpause']   = int(SITES[SITE]['checkpause'])
    SITES[SITE]['lastasked']    = 0
    SITES[SITE]['lastchecked']  = 0
    SITES[SITE]['lastmodified'] = 0
    if SITES[SITE].has_key('channels') :
      SITES[SITE]['channels'] = SITES[SITE]['channels'].split(',')
else :
  raise Exception('no config loaded; missing %s ?' % INI_FILE)
del(CONF, INI_FILE, INI_LOADED) # don't wait for GC that won't happen


def _latestSBaHJpath ():
  # special case.  The path changes on every update
  # TODO: config setting for a regexp to search sites the proper path
  #       so that any SITE[] can have this, not just Sweet Bro and Hella Jeff
  conn = httplib.HTTPConnection('mspaintadventures.com', timeout=1)
  conn.request('GET', '/sweetbroandhellajeff/')
  text = conn.getresponse().read()
  j = text.find('"><img src="new.jpg"')
  i = text.rfind('=', 0, j)
  if i > 0 and j > 0 :
    newn = '/sweetbroandhellajeff/archive/%s' % text[i+1:j]
    print '... checking', newn
    return newn
  else:
    print "... didn't find the sbahj new.jpg link"
    return False

def _secsToPretty(ticks=0):
  " given ticks as a duration in seconds, convert it to human-friendly units "
  day, remain    = divmod(ticks, (24*60*60))
  hour, remain   = divmod(remain, (60*60))
  minute, second = divmod(remain, 60)
  if (day > 0):
    return "%dd %dh" % (day, hour)
  elif (hour > 0):
    return "%dh %dm" % (hour, minute)
  elif (minute > 0):
    return "%dm %ds" % (minute, second)
  else:
    return "less than a minute"

def _getLastModified(site):
  """ given a key for the SITES[] global dict dict, returns age in seconds
  if request is less than SITES[]['checkpause'] ago, returns cached answer
  """
  now = time.mktime(time.gmtime())
  if (now >= (SITES[site]['lastchecked']+SITES[site]['checkpause'])):
    if (site == 'sbahj'):
      # special case
      urpdoot = _latestSBaHJpath()
      if urpdoot :
        SITES[site]['path'] = urpdoot
    conn = httplib.HTTPConnection(SITES[site]['host'], timeout=3)
    conn.request("HEAD", SITES[site]['path'])
    res = conn.getresponse()
    last_modified = res.getheader('Last-Modified')
    if last_modified:
      timetuple = rfc822.parsedate(last_modified)
      SITES[site]['lastmodified'] = time.mktime(timetuple)
      SITES[site]['lastchecked'] = now
  return SITES[site]['lastmodified']

def checkCommand(word, word_eol, userdata):
  """ respond to "/(SITES[]['command'])" messages
      prints to local client window
  """
  del(word_eol, userdata) # shut up, pylint
  flair = ''
  site = ''
  for i in SITES:
    if (SITES[i].has_key('command') and word[0] == SITES[i]['command']):
      site = i
  if (site == ''):
    print "huh? no site with matching command:", word[0]
    return xchat.EAT_NONE
  if SITES[site].has_key('flair'):
    flair = SITES[site]['flair']
  now = time.mktime(time.gmtime())
  modtime = _getLastModified(site)
  if (modtime):
    print "%s updated \002%s\002 ago%s" % (SITES[site]['name'], _secsToPretty(now-modtime), flair)
  else:
    print "%s couldn't get a decent update; try again later?" % SITES[site]['name']
  return xchat.EAT_ALL

def checkCommandEmote(word, word_eol, userdata):
  """ respond to "/(SITES[]['command'])_emote" messages
      emotes to current context
  """
  del(word_eol, userdata) # shut up, pylint
  flair = ''
  site = ''
  for i in SITES:
    if (SITES[i].has_key('command') and word[0] == SITES[i]['command']+'_emote'):
      site = i
  if (site == ''):
    print "huh? no site with matching command:", word[0]
    return xchat.EAT_NONE
  if SITES[site].has_key('flair'):
    flair = SITES[site]['flair']
  now = time.mktime(time.gmtime())
  modtime = _getLastModified(site)
  if (modtime):
    xchat.command("me is certain %s updated \002%s\002 ago%s"
                  % (SITES[site]['name'], _secsToPretty(now-modtime),flair)
                 )
    SITES[site]['lastasked'] = now
  else:
    print "%s couldn't get a decent update; try again later?" % SITES[site]['name']
  return xchat.EAT_ALL

def _in_list_or_string(needle, haystack):
  # because 'needle' in 'haystackneedle' returns True
  if haystack == None:
    return False
  if (type(haystack) == (type({}))):
    return needle in haystack
  elif (type(haystack) in (type(()), type([]))):
    return needle in haystack
  elif (type(haystack) == type('')):
    return needle == haystack
  else:
    raise TypeError('unknown haystack type:', type(haystack))

def checkPrint(word, word_eol, userdata):
  """ if it matches SITES[]['trigger'],
      if it's been SITES[]['askpause'] since last, respond with an emote.
      if it's less than that since last, respond with a privmsg.
  """
  del(word_eol, userdata) # shut up, pylint
  context = xchat.get_context()
  chan = context.get_info('channel')
  cmd = word[1].split(' ')[0]
  if cmd == '':
    return None
  flair = ''
  site_key = None
  for site in SITES:
    if SITES[site].get('trigger') == cmd :
      if (SITES[site].has_key('channels')
          and _in_list_or_string(chan,SITES[site]['channels'])
         ):
        site_key = site
      else:
        # else no channels are mentioned
        site_key = site
  if not site_key:
    return None
  site = SITES[site_key]
  flair = site.get('flair','')

  now = time.mktime(time.gmtime())
  modtime = _getLastModified(site_key)
  message = ''
  if (modtime):
    message = "%s updated \002%s\002 ago%s" % (site['name'], _secsToPretty(now-modtime), flair)
  else:
    message = "%s update wasn't found; try again later." % site['name']
    xchat.command('msg %s %s' % (word[0], message))
    return xchat.EAT_PLUGIN
  if (now < site['lastasked']+site['askpause']):
    xchat.command('msg %s %s' % (word[0], message))
  else:
    context.command("me is certain %s" % message)
    site['lastasked'] = now
  return xchat.EAT_PLUGIN


# -- main
print "\002Loaded %s v%s\002" % (__module_name__, __module_version__)
CLIST = ''
for SITE in SITES:
  if SITES[SITE].has_key('command'):
    xchat.hook_command(SITES[SITE]['command'], checkCommand , help='show you %s age' % SITES[SITE]['name'])
    CLIST += '/' + SITES[SITE]['command'] + ' '
    xchat.hook_command(SITES[SITE]['command']+'_emote', checkCommandEmote , help='announces %s age' % SITES[SITE]['name'])
    CLIST += '/' + SITES[SITE]['command'] + '_emote '
print "\002commands:\002", CLIST

CLIST = ''
xchat.hook_print('Channel Message', checkPrint)
xchat.hook_print('Your Message', checkPrint)
for SITE in SITES:
  if SITES[SITE].has_key('trigger'):
    CLIST += SITES[SITE]['trigger'] + ' '
print "\002triggers:\002", CLIST

del(CLIST, SITE) #  don't wait for GC that will never happen

