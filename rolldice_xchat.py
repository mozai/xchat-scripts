"""
  this is a python script for use with hexchat
  yeah yeah everyone has a dice-rolling thing
"""
import random
import re
import time
import hexchat
__module_name__ = "dice"
__module_version__ = "20160412"
__module_description__ = "roll the bones."
__module_author__ = "Mozai <moc.iazom@sesom>"

TIMEOUT = 1
CHANNELS = ('#wetfish', '#test', '#farts')
TIMEOUTS = {i: 0 for i in CHANNELS}


def _roll(what):
  results = []
  for i in what:
    match = re.search(r'^(\d+)$', i)
    if match:
      results.append(str(random.randint(1, int(match.group(1)))))
      continue
    match = re.search(r'^(\d*)d(\d+)([+-]\d+)?$', i)
    if match:
      n = match.group(1)
      eachroll = []
      if not n:
        n = 1
      for j in range(int(n)):
        eachroll.append(random.randint(1, int(match.group(2))))
      if match.group(3):
        eachroll.append(int(match.group(3)))
      sumroll = sum([j for j in eachroll])
      results.append(','.join([str(j) for j in eachroll]) + ' = ' + str(sumroll))
      continue
    match = re.search(r'^(\d*)dF$', i)
    if match:
      faces = ('-', '0', '+')
      n = match.group(1)
      if not n:
        n = 4
      eachroll = []
      for j in range(int(n)):
        eachroll.append(random.randint(0, 2))
      sumroll = sum([j for j in eachroll]) - n
      if sumroll >= 0:
        sumroll = '+' + str(sumroll)
      eachroll.sort()
      results.append(''.join([faces[j] for j in eachroll]) + ':' + str(sumroll))
      continue
    results.append(i + '?')
  return '  '.join(results)


def checkCommand(word, word_eol, userdata):
  del(word_eol, userdata)  # shut up, pylint
  if word[1:]:
    print("rolled dice: " + _roll(word[1:]))
  else:
    print("rolled dice: " + _roll(['2d6']))
  return hexchat.EAT_PLUGIN
hexchat.hook_command('roll', checkCommand, help='roll the bones, XdY+Z')
hexchat.hook_command('dice', checkCommand, help='roll the bones, XdY+Z')


def checkPrint(word, word_eol, userdata):
  del(word_eol, userdata)  # shut up pylint
  now = int(time.time())
  context = hexchat.get_context()
  chan = context.get_info('channel')
  if chan not in TIMEOUTS:
    return hexchat.EAT_NONE
  # who = word[0]
  if len(word) < 2:
    return None
  words = word[1].strip().split()
  if len(words) < 1:
    # degenerate case of "nick PRIVMSG #channel :\r\n"
    return None
  if words[0] in ('.dice', '.roll'):
    if now <= TIMEOUTS[chan]:
      return hexchat.EAT_NONE
    if len(words) < 2:
      words.append('2d6')
    print(repr(words))
    result = _roll(words[1:])
    if result:
      TIMEOUTS[chan] = now + TIMEOUT
      context.command("me rolls " + result)
      return hexchat.EAT_PLUGIN
hexchat.hook_print('Channel Message', checkPrint)
hexchat.hook_print('Your Message', checkPrint)

print("{} loaded (/roll, .roll)".format(__module_name__))
