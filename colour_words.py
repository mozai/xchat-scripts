""" Example plugin to show odd print_emit() behaviour
"""

# -- config
HIGHLIGHTS = [
  # if this was a real module, I'd make this an easy-to-read config
  [ 'black',  '\00300,01' ],
  [ 'blue',   '\00300,02' ],
  [ 'green',  '\00301,03' ],
  [ 'red',    '\00300,04' ],
]

# -- init
__module_name__  = "colour_words"
__module_version__  = "20130121"
__module_description__  = "Highlights some words"
__module_author__  =  "Mozai <moc.iazom@sesom>"
import re, xchat

# \003<foreground>,<background>
MIRC_COLOURS = {
  'normal':'\017', 'bold':'\002', 'underline':'\037',
  'reverse':'\026', 'italic':'\026', 'beep':'\007',
  'white':'\00300',  'black':'\00301',  'blue':'\00302',
  'green':'\00303',  'red':'\00304',    'maroon':'\00305',
  'purple':'\00306', 'orange':'\00307', 'yellow':'\00308',
  'lime':'\00309',   'teal':'\00310',   'cyan':'\00311',
  'royal':'\00312',  'pink':'\00313',   'grey':'\00314', 
  'silver':'\00315',
}
MIRC_COLOUR_RESET = MIRC_COLOURS['normal']

def nick_to_prefix(nick):
  " john -> @ "
  userlist = xchat.get_list('users')
  for i in userlist:
    if xchat.nickcmp(nick, i.nick) == 0 :
      return i.prefix

def colour_words(word, word_eol, userdata):
  " Recolour some users's messages "
  del(userdata) # shoosh, pylint
  # if the incoming message is ":nick!name@host PRIVMSG :message payload"
  # then word = ["nick","message payload"]
  # and word_eol = ["nick message payload", "message payload"]
  # word_eol omits '!name@host PRIVMSG :' but does NOT break the message
  # payload on whitespace, like it does with '/command'.  Weird.
  nick = word[0]
  mesg = word[1]
  old_mesg = mesg
  for high in HIGHLIGHTS:
    mesg = high[0].sub(r'%s\1%s' % (high[1], MIRC_COLOUR_RESET), mesg)
  if mesg == old_mesg :
    # no change, maybe because we've already seen it
    return xchat.EAT_NONE
  else:
    # I had to go to the GUI to dig out the params for 'Channel Message'
    # why is this not documented?  And why is "mode char" unused, but
    # "identified text" is where I expect the user's mode char to be?
    # Channel Message - 1:Nickname, 2:The text, 3:Mode char, 4:Identified text
    # Result - %C18%H<%H$4$1%H>%H%O$t$2
    xchat.emit_print("Channel Message", nick, mesg, nick_to_prefix(nick), '')
    return xchat.EAT_ALL
  return xchat.EAT_NONE

# -- main
for j in range(len(HIGHLIGHTS)):
  # convert in-place into a regexp that includes colour format codes
  HIGHLIGHTS[j][0] = re.compile('(?:\003' + r'\d+(?:,\d+)?)?\b(%s)\b(?:' % HIGHLIGHTS[j][0] + '\017' + r')?' , re.I)

xchat.hook_print('Channel Message', colour_words)

print "loaded %s v%s" % (__module_name__, __module_version__)

