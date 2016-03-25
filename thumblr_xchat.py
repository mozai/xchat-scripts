"""
  this is a python script for use with xchat v2.x.
  I had to change a certain name to tu\x6D\x62lr
  because of some anti-spam that auto-blocks any urls with that name
"""

# -- init
__module_name__ = "thumblr"
__module_version__ = "20150319"
__module_description__ = "image url burp"
__module_author__ = "Mozai <moc.iazom@sesom>"
import xchat
import re, threading, time, urllib
from bs4 import BeautifulSoup

# -- config
# timeout between command responses
# bots shouldn't spam, even when asked to
COOLDOWN = 60
CHANNELS = ['#farts', '#wetfish', '#test', '#mbtest']
TRIGGER = '!thumblr'
THUMBLR_URL = 'http://www.tu\x6D\x62lr.com/tagged/%s'
USER_AGENT = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'
DEFAULT_TAG = 'homestuck'
# -- end config

LASTTIME = dict()
for i in CHANNELS:
  LASTTIME[i] = 0


class DontBeRacist(urllib.FancyURLopener):
  " to avoid discrimination against bots "
  version = USER_AGENT

urllib.open = DontBeRacist().open
urllib.urlretrieve = DontBeRacist().retrieve


def _force_to_int(text):
  return int('0' + ''.join([i for i in text if i.isdigit()]))


def fetch_posts(tag, count=16):
  """ returns a list of dict
  tag can be any simple word, whitespaces become one '-' dash
  dict has keys ('href', 'photo_stage_img', 'notes', 'tags')
  """
  tag = re.sub(r'[^a-z0-9]+', '-', tag.lower())
  tag = re.sub(r'^\-|\-$', '', tag)
  url_to_use = THUMBLR_URL % tag
  response = urllib.open(url_to_use)
  soup = BeautifulSoup(response.read(), 'html.parser')
  posts_found = []
  for node1 in soup.find_all('li', 'post'):
    post = {'href': None, 'photo_stage_img': None, 'tags': [], 'notes': 0}
    node2 = node1.find('div', 'photo_stage_img')
    if node2:
      mobj = re.search(r'url\((.*?)\)', node2.get('style', ''))
      if mobj:
        post['photo_stage_img'] = mobj.group(1)
    node2 = node1.find('a', 'click_glass')
    if node2:
      post['href'] = node2['href'][:node2['href'].rindex('/')]
      post['href'] = post['href'].replace('https:', 'http:', 1)
    post['tags'] = []
    for node2 in node1.find('a', 'post_tag'):
      post['tags'].append(node2.replace(' ', '-'))
    node2 = node1.find('a', 'notes')
    if node2:
      post['notes'] = _force_to_int(node2.text)
    if 'photo_stage_img' in post:
      posts_found.append(post)
      count -= 1
      if count <= 0:
        break
  return posts_found


def thumblrCommand(word, word_eol, userdata):
  """ respond to "/thumblr (command)" messages
      prints to local client window
  """
  del(word_eol, userdata)  # shut up, pylint
  if len(word) == 1:
    print "/thumblr tagname ie.: '/thumblr cosplay'"
  elif len(word) == 2:
    foundposts = fetch_posts(word[1], 1)
    if foundposts:
      blurb = "Have a look at %s" % foundposts[0]['photo_stage_img']
      print blurb
  return xchat.EAT_ALL


xchat.hook_command('thumblr', thumblrCommand, help='/thumblr tagname - gives URL')


def _search_and_emit(context, tagname):
  " (thread) search for 'phrase' images, emit result to xchat context "
  foundposts = fetch_posts(tagname, 1)
  blurb1 = "\x02\x0302tu\x6Dblr\x0F {}"
  if foundposts:
    blurb2 = foundposts[0]['photo_stage_img']
    # Indexer insists
    blurb2 = blurb2.replace('_500.jpg', '_1280.jpg')
    blurb2 = blurb2.replace('_500.png', '_1280.png')
  else:
    blurb2 = "(didn\'t find anything for {}".format(tagname)
  context.command("say " + blurb1.format(blurb2))
  return None


def checkPrint(word, word_eol, userdata):
  " if someone says '!thumblr somephrase', respond like '/thumblr_say somephrase' "
  del(word_eol, userdata)  # shut up, pylint
  now = int(time.time())
  context = xchat.get_context()
  chan = context.get_info('channel')
  if ((len(CHANNELS) > 0) and (chan not in CHANNELS)):
    return None
  words = word[1].split()
  if len(words) < 2 or words[0] != TRIGGER:
    return
  tagname = words[1].lstrip('#')
  if not tagname:
    return
  if LASTTIME[chan] + COOLDOWN >= now:
    # tell requester to wait
    context.command('msg %s %s timeout is %d seconds' % (word[0], TRIGGER, COOLDOWN))
    return xchat.EAT_PLUGIN
  # I'm doing something a little thread unsafe here, because I'm trusting
  # the 'LASTTIME + COOLDOWN' above to keep too many threads
  # from running at once
  drone = threading.Thread(target=_search_and_emit, args=(context, tagname))
  drone.daemon = True  # allow parent to abandon this child
  drone.start()  # go do your thing while I go away
  LASTTIME[chan] = now
  return xchat.EAT_PLUGIN


LASTTIME[TRIGGER] = 0
xchat.hook_print('Channel Message', checkPrint)
xchat.hook_print('Your Message', checkPrint)


# -- main
print "\x02Loaded %s v%s\x02" % (__module_name__, __module_version__)
print "\x02commands:\x02 /thumblr tagname"
print "\x02listens:\x02 {} tagname".format(TRIGGER)
