"""
  this is a python script for use with xchat v2.x.
"""

# -- init
__module_name__ = "search_yt"
__module_version__ = "20151008"
__module_description__ = "Search YouTube"
__module_author__ = "Mozai <moc.iazom@sesom>"
import json
import time
import urllib
import xchat

API_KEY = "get your own"
TIMEOUT = 60  # seconds between emotes
LASTUSED = {'#test': 0, '#farts': 0}  # also list of allowed channels

# import os; print os.getcwd()  # QUACK

APIKEY = open('.xchat2/search_youtube_xchat.apikey.txt').read().strip()
# TODO: there has to be a way for xchat to tell me where this script was loaded from
APIURL = 'https://www.googleapis.com/youtube/v3/search?part=snippet&q={}&type=video&fields=items(id%2Csnippet%2Ftitle%2Csnippet%2FpublishedAt)&key=' + APIKEY
# 'order' paramter: ('relevance', 'date', 'rating', 'title', 'viewCount')
YOUTUBELOGO = "\x0301,00You\x0300,04Tube\x0f"


def fetchYTresults(searchterms):
  " return list of {id:'', publishedAt:'', title:''} "
  try:
    res = urllib.urlopen(APIURL.format(urllib.quote_plus(searchterms)))
    google_api_answer = json.loads(res.read())
    res.close()
    return [
       {'id': i['id']['videoId'], 'publishedAt': i['snippet']['publishedAt'], 'title': i['snippet']['title'][:60].strip()}
       for i in google_api_answer['items']
    ]
  except Exception as e:
    print e
    return [{'id': '', 'publishedAt': '', 'title': repr(e)}, ]


def checkCommand(word, word_eol, userdata):
  """ respond to "/yt (search terms)" messages
      prints to local client window
  """
  del(userdata)  # shut up, pylint
  if len(word) > 1:
    params = word_eol[1]
    found = fetchYTresults(params)[0]
    if found['id']:
      print '{} {} \x1fhttp://youtu.be/{}\x0f'.format(YOUTUBELOGO, found['title'], found['id'])
    else:
      print '*** error searching YouTube: {}'.format(found['title'])
  else:
    print "/yt some words here. ie.: '/yt kittens cute pumpkin'"
  return xchat.EAT_ALL


def checkPrint(word, word_eol, userdata):
  " if someone says '.yt', respond like 'found http://youtu.be/asdf "
  del(word_eol, userdata)  # shut up, pylint
  # "PRIVMSG Jane :that smells bad"
  # word[0] = 'Jane' word[1] = 'that smells bad'
  # word_eol[0] = 'Jane that smells bad' word_eol[1] = 'that smells bad'
  if ' ' in word[1]:
    cmd, params = word[1].split(' ', 1)
  else:
    cmd, params = word[1], None
  context = xchat.get_context()
  chan = context.get_info('channel')
  if cmd == '!yt': 
    if not params:
      return xchat.NONE
    if chan in LASTUSED:
      now = time.time()
      if LASTUSED[chan] + TIMEOUT >= now:
        context.command('msg {} "!yt" on cooldown'.format(word[0]))
      else:
        found = fetchYTresults(params)[0]
        if found['id']:
          context.command('me found \x02{}\x0f \x1fhttp://youtu.be/{}\x0f'.format(found['title'], found['id']))
        else:
          context.command('me couldn\'t search YouTube')
          print '*** error searching YouTube: {}'.format(found['title'])
        LASTUSED[chan] = now
    return xchat.EAT_PLUGIN


# -- main
print "\x02Loaded %s v%s\x02" % (__module_name__, __module_version__)
xchat.hook_print('Channel Message', checkPrint)
xchat.hook_print('Your Message', checkPrint)
xchat.hook_command('yt', checkCommand, help='"/yt" for help')
print "\x02commands:\x02 /yt"
print "\x02triggers:\x02 !yt"
