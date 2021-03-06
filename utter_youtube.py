"""
  this is a python script for use with xchat v2.x.
"""
# 2016-02-17 : YouTube changed their API, they're making 'textDisplay'
#    into an empty string
# 2016-03-21 : now with threading so it won't lock up xchat during search
import HTMLParser
import json
from random import random
import re
import threading
import time
import urllib
import xchat

# -- init
__module_name__ = "utter_yt"
__module_version__ = "20160321"
__module_description__ = "Utter YouTube"
__module_author__ = "Mozai <moc.iazom@sesom>"
API_KEY = "get your own"
TIMEOUT = 5  # seconds between emotes
CHANNELS = ('#test', '#farts', '#wetfish')
LASTUSED = {'#test': 0, '#farts': 0, '#wetfish': 0}  # also the list of allowed channels
CHANCE = 0.02  # %age it will chatter, too high will get you banned

try:
  # cwd is different if a module is loaded automatically or manually
  # xchat2 is kinda silly about that
  APIKEY = open('search_youtube_xchat.apikey.txt').read().strip()
except IOError:
  APIKEY = open('.xchat2/search_youtube_xchat.apikey.txt').read().strip()
APIURL1 = 'https://www.googleapis.com/youtube/v3/search?part=snippet&q={}&type=video&fields=items(id)&key=' + APIKEY
# I want items[0]['id']
APIURL2 = 'https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&maxResults=1&order=relevance&textFormat=plainText&videoId={}&key=' + APIKEY
# I want items[0]['snippet']['toplevelComment']['snippet']['textDisplay']
YOUTUBELOGO = "\x0301,00You\x0300,04Tube\x0f"
HTMLPARSER = HTMLParser.HTMLParser()  # god this is dumb just to get unescape()
LASTUSED = {i:0 for i in CHANNELS}


def fetchYTcomment(searchterms):
  " return string that is top comment for some video "
  try:
    searchterms = re.sub('[^a-z]', ' ', searchterms.lower())
    searchterms = re.sub('\s+', ' ', searchterms)
    searchterms = searchterms.strip()
    res = urllib.urlopen(APIURL1.format(urllib.quote_plus(searchterms)))
    google_api1_answer = json.loads(res.read())
    res.close()
    #print "API answer 1 : " + repr(google_api1_answer)
    topComment = ''
    for item in google_api1_answer['items']:
      videoId = item['id']['videoId']
      res = urllib.urlopen(APIURL2.format(urllib.quote_plus(videoId)))
      google_api2_answer = json.loads(res.read())
      #print "API answer 2 : " + repr(google_api2_answer)
      res.close()
      if len(google_api2_answer['items']) >= 1:
        snippet = google_api2_answer['items'][0]['snippet']['topLevelComment']['snippet']
        topComment = snippet['textDisplay']
        if topComment == '' or topComment == u'':
          continue
        topComment = HTMLPARSER.unescape(topComment)
        topComment = topComment.encode('utf8')
        topComment = re.sub('<.*?>', ' ', topComment)
        topComment = re.sub('\s+', ' ', topComment)
        return topComment
    return None
  except Exception as e:
    print e
    return None


def checkCommand(word, word_eol, userdata):
  del(userdata)  # shut up, pylint
  if len(word) > 1:
    wisdom = fetchYTcomment(word_eol[1])
    print '{} {}'.format(YOUTUBELOGO, wisdom)
  else:
    print "/ytbabble give me something to work with, eh?"
  return xchat.EAT_ALL

def _barker(context, phrase):
  wisdom = fetchYTcomment(phrase)
  if wisdom:
    # context.command('say {}'.format(wisdom))
    context.prnt('{} \x0315"{}"\x0f'.format(YOUTUBELOGO, wisdom))
  else:
    context.prnt('{} \x0315(nothing found?)\x0f'.format(YOUTUBELOGO))
    pass


def checkPrint(word, word_eol, userdata):
  " listen to everything said, sometimes blurt out YouTube wisdom "
  del(word_eol, userdata)  # shut up, pylint
  # "PRIVMSG Jane :that smells bad"
  # word[0] = 'Jane' word[1] = 'that smells bad'
  # word_eol[0] = 'Jane that smells bad' word_eol[1] = 'that smells bad'
  context = xchat.get_context()
  chan = context.get_info('channel')
  if chan not in LASTUSED:
    return None
  now = time.time()
  if LASTUSED[chan] + TIMEOUT >= now:
    # on cooldown
    return None
  if random() > CHANCE:
    # rolled dice, not now
    return None
  drone = threading.Thread(target=_barker, args=(context, word[1]))
  drone.daemon = True  # permit death of parent
  drone.start()
  LASTUSED[chan] = now
  return xchat.EAT_PLUGIN



# -- main
print "\x02Loaded %s v%s\x02" % (__module_name__, __module_version__)
xchat.hook_print('Channel Message', checkPrint)
xchat.hook_command('ytbabble', checkCommand, help='/ytbabble string (for testing only)')
print "\x02commands:\x02 /ytbabble some_text".format(CHANCE)
print "\x02triggers:\x02 any text, {}/1.0 % chance of response.".format(CHANCE)
