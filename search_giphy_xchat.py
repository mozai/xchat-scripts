"""
  this is a python script for use with xchat v2.x.
"""

# -- init
__module_name__ = "search_giphy"
__module_version__ = "20151011"
__module_description__ = "Search Giphy"
__module_author__ = "Mozai <moc.iazom@sesom>"
import json
import time
import urllib
import xchat

API_KEY = "get your own"
TIMEOUT = 60  # seconds between emotes
LASTUSED = {'#test': 0, '#farts': 0}  # also list of allowed channels

# import os; print os.getcwd()  # QUACK

APIKEY = open('.xchat2/search_giphy_xchat.apikey.txt').read().strip()
# TODO: there has to be a way for xchat to tell me where this script was loaded from
APIURL = 'http://api.giphy.com/v1/gifs/random?tag={}&api_key=' + APIKEY
# APIURL = http://api.giphy.com/v1/gifs/search?limit=1&q={}&api_key=' + APIKEY
# q: searchphrase, limit: number, offset: number, rating (y, g, pg, pg-13, r)


def fetchAPIresults(searchterms):
  " return  url to dumb picture "
  # /gifs/random returns just one item
  # /gifs/search returns many items and
  try:
    url = APIURL.format(urllib.quote_plus(searchterms))
    res = urllib.urlopen(url)
    api_answer = json.loads(res.read())
    res.close()
    api_answer = api_answer['data']
    if isinstance(api_answer, list):
      return api_answer[0]['embed_url']
    else:
      return api_answer['image_original_url']
  except Exception as e:
    print e
    return ''


def checkCommand(word, word_eol, userdata):
  """ respond to "/yt (search terms)" messages
      prints to local client window
  """
  del(userdata)  # shut up, pylint
  if len(word) > 1:
    params = word_eol[1]
    found = fetchAPIresults(params)
    if found:
      print 'GIPHY found \x1f{}\x0f'.format(found)
    else:
      print '*** error searching Giphy.'
  else:
    print "/giphy some words here. ie.: '/giphy kittens cute pumpkin'"
  return xchat.EAT_ALL


def checkPrint(word, word_eol, userdata):
  " if someone says '.giphy', respond like 'found http://blah.gif "
  del(word_eol, userdata)  # shut up, pylint
  if ' ' in word[1]:
    cmd, params = word[1].split(' ', 1)
  else:
    cmd, params = word[1], None
  context = xchat.get_context()
  chan = context.get_info('channel')
  if cmd == '!giphy':
    if not params:
      return xchat.NONE
    if chan in LASTUSED:
      now = time.time()
      if LASTUSED[chan] + TIMEOUT >= now:
        context.command('msg {} "!giphy" on cooldown'.format(word[0]))
      else:
        found = fetchAPIresults(params)
        if found:
          context.command('me found \x1f{}\x0f'.format(found))
        else:
          context.command('me couldn\'t search Giphy')
          print '*** error searching Giphy'
        LASTUSED[chan] = now
    return xchat.EAT_PLUGIN


# -- main
print "\x02Loaded %s v%s\x02" % (__module_name__, __module_version__)
xchat.hook_print('Channel Message', checkPrint)
xchat.hook_print('Your Message', checkPrint)
xchat.hook_command('giphy', checkCommand, help='"/giphy" for help')
print "\x02commands:\x02 /giphy"
print "\x02triggers:\x02 !giphy"
