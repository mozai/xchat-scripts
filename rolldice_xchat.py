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

TIMEOUT = 2
CHANNELS = '#wetfish #test #farts #botspam'.split()
TIMEOUTS = {i: 0 for i in CHANNELS}


def _roll(what):
  results = []
  for i in what:

    # pick a number between 1 and n "d13" or just "13"
    match = re.search(r'^(\d+)$', i)
    if match:
      x = int(match.group(1))
      result = "d{} = {}".format(x, random.randint(1, x))
      if len(result) > 128:
        result = '(answer too large)'
      results.append(result)
      continue

    # D&D dice, "3d6+2"
    match = re.search(r'^(\d*)d(\d+)([+-]\d+)?$', i)
    if match:
      n = int(match.group(1) or '1')
      m = int(match.group(2))
      o = int(match.group(3) or '0')
      eachroll = []
      for j in range(int(n)):
        eachroll.append(random.randint(1, m) + o)
      sumroll = sum([j for j in eachroll])
      result = '{} = {} = {}'.format(match.group(0),  ','.join([str(j) for j in eachroll]), str(sumroll))
      if len(result) > 128:
        result = '{} = {}'.format(match.group(0), sumroll)
      if len(result) > 128:
        result = '(answer too large)'
      results.append(result)
      continue

    # Fate dice, "4dF"
    match = re.search(r'^(\d*)dF$', i)
    if match:
      faces = ('-', '_', '+')
      n = int(match.group(1) or '4')
      eachroll = []
      for j in range(int(n)):
        eachroll.append(random.randint(0, 2))
      sumroll = sum([j for j in eachroll]) - n
      if sumroll >= 0:
        sumroll = '+' + str(sumroll)
      eachroll.sort()
      result = '{} = {} = {}'.format(match.group(0), ''.join([faces[j] for j in eachroll]), sumroll)
      if len(result) > 128:
        result = '(answer too large)'
      results.append(result)
      continue

    # TODO: Greg Stolze's One-Roll-Engine (ORE)
    # rolls nd10, sort and group them into matching sets
    # '.roll 9ore10' -> '5-5-5 7-7 6-6 9 8 2'
    # '9ore' assumes '9ore10'  'oreX' assumes '(X-1)oreX'
    # cannot roll more dice than faces on each die

    # else unrecognized method
    results.append(i + '?')

  answer = '; '.join(results)
  if len(answer) > 500:
    answer = "(response too large)"
  return answer


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
