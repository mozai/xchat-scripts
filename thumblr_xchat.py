"""
  this is a python script for use with xchat v2.x.
"""

# -- init
__module_name__ = "thumblr"
__module_version__ = "20141121"
__module_description__ = "image url burp"
__module_author__ = "Mozai <moc.iazom@sesom>"
import xchat
import re, time, urllib
from bs4 import BeautifulSoup

# -- config
# timeout between command responses
# bots shouldn't spam, even when asked to
COOLDOWN = 120
THUMBLR_URL = 'http://www.tu\x6D\x62lr.com/tagged/%s'
USER_AGENT = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'
DEFAULT_TAG = 'homestuck'
# -- end config

LASTTIME = dict()


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
  response = urllib.open(THUMBLR_URL % tag)
  soup = BeautifulSoup(response.read())
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
  """ respond to "/hsg (command)" messages
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


def checkPrint(word, word_eol, userdata):
  " if someone says '.hsg', respond like '/hsg co' "
  del(word_eol, userdata)  # shut up, pylint
  now = int(time.time())
  context = xchat.get_context()
  #chan = context.get_info('channel')
  #if ((len(channels) > 0) and (chan not in channels)):
  #  return None
  if not word[1].startswith('!thumblr '):
    return
  cmd, tagname = word[1].split(' ', 1)
  if ' ' in tagname:
    tagname = tagname[:tagname.index(' ')]
  tagname = tagname.lstrip('#')
  if not tagname:
    return
  if LASTTIME[cmd] + COOLDOWN >= now:
    context.command('msg %s %s timeout is %d seconds' % (word[0], cmd, COOLDOWN))
    return xchat.EAT_PLUGIN
  foundposts = fetch_posts(tagname, 1)
  if foundposts:
    blurb = "\x02\x0302tu\x6Dblr\x0F %s" % foundposts[0]['photo_stage_img']
    context.command("say " + blurb)
    LASTTIME[cmd] = now
  else:
    context.command('msg %s %s didn\'t find anything for %s' % (word[0], cmd, tagname))
  return xchat.EAT_PLUGIN

LASTTIME['!thumblr'] = 0
xchat.hook_print('Channel Message', checkPrint)
xchat.hook_print('Your Message', checkPrint)


# -- main
print "\x02Loaded %s v%s\x02" % (__module_name__, __module_version__)
print "\x02commands:\x02 /thumblr tagname"
print "\x02listens:\x02 !thumblr tagname"
