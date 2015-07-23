# !8ball         :if someone says this, and timeout expired, /filthy_say

# -- config
# time between saying stuff out-loud
timeout = 120

# channels to listen for the '!filthy' trigger
channels = ['#farts', '#test', '#wetfish']

# -- init
__module_name__ = "eightball"
__module_version__ = "20150716"
__module_description__ = "Eightball"
__module_author__ = "Mozai <moc.iazom@sesom>"
import xchat, random, time

# IRC colours as per mIRC:
#   \x0301 black \x0302 blue \x0302,01 blue-on-black \x0f normal

ANSWERS = [
  # taken from a dissection of a Mattel toy: 10 yes, 5 no, 5 neutral
  'It is decidedly so',
  'You may rely on it',
  'Outlook good',
  'Yes definitely',
  'Signs point to yes',
  'Most likely',
  'Without a doubt',
  'Yes',
  'As I see it yes',
  'It is certain',
  'Very doubtful',
  'Outlook not so good',
  'My sources say no',
  'Dont count on it',
  'My reply is no',
  'Better not tell you now',
  'Concentrate and ask again',
  'Reply hazy try again',
  'Cannot predict now',
  'Ask again later'
]


def _eightball_name():
  return random.choice([
    u'magic Eight-ball\u2122'.encode('utf8'),
    '8ball',
    'eightball',
    u'\u277d'.encode('utf8')
    ])


def _get_answer():
  # global sentences
  return random.choice(ANSWERS)


def eightball(word, word_eol, userdata):
  del(word, word_eol, userdata)  # shut up pylint
  print "The %s says \x0300,02 %s \x0f" % (_eightball_name(), _get_answer())
  return xchat.EAT_ALL
xchat.hook_command('8ball', eightball, help='shake your personal 8-ball')
xchat.hook_command('eightball', eightball, help='shake your personal 8-ball')


def eightball_say(word, word_eol, userdata):
  del(word, word_eol, userdata)  # shut up, pylint
  xchat.command("me shakes the %s. \x0300,02 %s \x0f" % (_eightball_name(), _get_answer()))
  return xchat.EAT_ALL
xchat.hook_command('8ball_say', eightball_say, help='shake your eightball in public')


def eightball_trigger(word, word_eol, userdata):
  " when someone publically asks for something filthy "
  global LASTTIME
  now = int(time.time())
  context = xchat.get_context()
  chan = context.get_info('channel')
  if ((len(channels) > 0) and (chan not in channels)):
    return None
  cmd = word[1].split(' ')[0]
  if (cmd == '!eightball' or cmd == '!8ball'):
    if (LASTTIME + timeout <= now):
      eightball_say(word, word_eol, userdata)
      LASTTIME = now
    else:
      print "refusing to answer until %d seconds from now" % (LASTTIME + timeout - now)
    return xchat.EAT_PLUGIN
LASTTIME = 0
xchat.hook_print('Channel Message', eightball_trigger)
xchat.hook_print('Your Message', eightball_trigger)


print "eightball loaded (/eightball, /eithball_say, !eightball, !8ball)"
