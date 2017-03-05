"""
  this is a python script for use with hexchat
  I had to change a certain name to tu\x6D\x62lr
  because of github thinks this file is spam if it mentions the name
"""
# Python 3.x
import hexchat, re, threading, time, urllib.request
from bs4 import BeautifulSoup

# -- init
__module_name__ = "thumblr"
__module_version__ = "20170203"
__module_description__ = "image url burp"
__module_author__ = "Mozai <moc.iazom@sesom>"

# -- config
# timeout between command responses
# bots shouldn't spam, even when asked to
COOLDOWN = 60
CHANNELS = ['#farts', '#wetfish', '#test', '#homosuck' ]
TRIGGER = '!thumblr'
THUMBLR_URL = 'http://www.tu\x6D\x62lr.com/tagged/%s'
USER_AGENT = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'
DEFAULT_TAG = 'homestuck'
# -- end config

LASTTIME = dict()
for i in CHANNELS:
  LASTTIME[i] = 0

# tu\x6D\x62lr is bigoted about bots
URLOPENER = urllib.request.build_opener()
URLOPENER.addheaders = [('User-agent', USER_AGENT)]

def _force_to_int(text):
  return int('0' + ''.join([i for i in text if i.isdigit()]))


def search_tumblr_tags_for_img(tag, count=16):
  """ returns a list of dict
  tag can be any simple word, whitespaces become one '-' dash
  dict has keys ('href', 'photo_stage_img', 'notes', 'tags')
  """
  tag = re.sub(r'[^a-z0-9]+', '-', tag.lower())
  tag = re.sub(r'^\-|\-$', '', tag)
  url_to_use = THUMBLR_URL % tag
  response = URLOPENER.open(url_to_use)
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


def _search_and_emit(context, tagname):
  " (thread) search for 'phrase' images, emit result to hexchat context "
  foundposts = search_tumblr_tags_for_img(tagname, 1)
  if foundposts:
    fname = foundposts[0]['photo_stage_img']
    # Indexer insists
    fname = fname.replace('_500.jpg', '_1280.jpg')
    fname = fname.replace('_500.png', '_1280.png')
  else:
    fname = "(didn\'t find anything for {})".format(tagname)
  if context:
    context.command("say \x02\x0302tu\x6Dblr\x0F {}".format(fname))
  else:
    print("\x02\x0302tu\x6Dblr\x0F {}".format(fname))
  return None


def _create_drone(context, tagname):
  drone = threading.Thread(target=_search_and_emit, args=(context, tagname))
  drone.daemon = True  # allow parent to abandon this child
  drone.start()  # go do your thing while I go away


def thumblrCommand(word, word_eol, userdata):
  """ respond to "/thumblr (command)" messages
      prints to local client window
  """
  del(word_eol, userdata)  # shut up, pylint
  if len(word) == 1:
    # no parameter, help message
    print("{} tagname ie.: '{} cosplay'".format(word[0], word[0]))
  elif len(word) == 2:
    tagname = word[1]
    if word[0] == 'thumblr':
      _create_drone(None, tagname)
    elif word[0] == 'thumblr_say':
      _create_drone(hexchat.get_context(), tagname)
  return hexchat.EAT_ALL


hexchat.hook_command('thumblr', thumblrCommand, help='/thumblr tagname - gives URL')
hexchat.hook_command('thumblr_say', thumblrCommand, help='/thumblr tagname - gives URL')


def checkPrint(word, word_eol, userdata):
  " if someone says '!thumblr somephrase', respond like '/thumblr_say somephrase' "
  del(word_eol, userdata)  # shut up, pylint
  now = int(time.time())
  context = hexchat.get_context()
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
    return hexchat.EAT_PLUGIN
  LASTTIME[chan] = now
  # I'm trusting the 'LASTTIME + COOLDOWN' above to keep too many threads
  # from running at once
  _create_drone(context, tagname)
  return hexchat.EAT_PLUGIN


LASTTIME[TRIGGER] = 0
hexchat.hook_print('Channel Message', checkPrint)
hexchat.hook_print('Your Message', checkPrint)


# -- main
print("\x02Loaded {} v{}\x02".format(__module_name__, __module_version__))
print("\x02commands:\x02 /thumblr tagname, /thumblr_say tagname")
print("\x02listens:\x02 {} tagname".format(TRIGGER))
