""" Changes the colour of some users's text.
   because there's an incessant narcicist I want to /ignore,
   but it's too damn confusing because she talks all the time and
   people respond to her.
"""
# TODO: load config from disk, mod config live, save config to disk

# -- config

# key is an IRC mask
#  (why isn't there something in xchat for matching? I gotta cook this
#   into a re.compile() to make it work. foo.)
# colour is an int for mIRC colour codes
# channels is a list; omit for 'all channels'

PEOPLE = {
  '*!*@Rizon-A43DFFC5.gwi.net': { 'colour': 'maroon' },
  '*!*@Rizon-5380BFEC.org': { 'colour': 'maroon' },
  '*!*@Rizon-87FC9C6.burl.east.myfairpoint.net': { 'colour': 'maroon' },
  '*!*@94756A2A.E41A0DC3.4B34C0C0.IP': { 'colour': 'maroon' },
  '*!*@*.maine.res.rr.com': { 'colour': 'maroon' },
  '*!Ross@*.myvzw.com': { 'colour': 'purple' }
}
# 'HSE!*@*.myfairpoint.net': { 'colour': 'maroon' },
# 'moses!*@deunan': { 'colour': '\00309,02' },

# -- init
__module_name__  = "coloured_people"
__module_version__  = "20130111"
__module_description__  = "Changes colour of some people's text"
__module_author__  =  "Mozai <moc.iazom@sesom>"
import re, xchat

MIRC_COLOURS = {
  'normal':'\017', 'bold':'\002', 'underline':'\037',
  'reverse':'\026', 'italic':'\026', 'beep':'\007',
# \003<fore>,<back>
  'white':'\00300',  'black':'\00301',
  'blue':'\00302',   'green':'\00303',  'red':'\00304',
  'maroon':'\00305', 'purple':'\00306', 'orange':'\00307',
  'yellow':'\00308', 'lime':'\00309',   'teal':'\00310',
  'cyan':'\00311',   'royal':'\00312',  'pink':'\00313',
  'grey':'\00314',   'silver':'\00315',
}
MIRC_COLOUR_RESET = '\017'
MIRC_COLOUR_FIND = re.compile('\003\\d+(,\\d+)?|\002|\037|\026|\007')

def ircglob_to_regexp(ircglob):
  """ Given nick!*@hostname, returns re.copile(r'^nick\!.+?@hostname$')
      Also catches some sloppy ircglobs
  """
  realglob = ircglob.strip()
  if '!' not in realglob:
    realglob = '*!' + realglob
  if '@' not in realglob:
    realglob = realglob.replace('!','!*@')
  if '!@' in realglob:
    realglob = realglob.replace('!@','!*@')
  if realglob.endswith('@'):
    realglob = realglob + '*'
  if realglob == '*!*@*':
    # if you want to shoot yourself in the foot, wrap this in try/catch-pass
    raise ValueError("Invalid ircglob: '%s' matches everybody" % ircglob)
  regexp = re.escape(realglob)
  regexp = r'^' + regexp.replace(r'\*','.+?') + r'$'
  return re.compile(regexp, re.I)

def nick_to_fullname(nick):
  " john -> john!~johnathan@johnson.com "
  userlist = xchat.get_list('users')
  for i in userlist:
    if xchat.nickcmp(nick, i.nick) == 0 :
      return "%s!%s" % (i.nick, i.host)

def nick_to_prefix(nick):
  " john -> @ "
  userlist = xchat.get_list('users')
  for i in userlist:
    if xchat.nickcmp(nick, i.nick) == 0 :
      return i.prefix

def colour_someone(word, word_eol, userdata):
  """ Recolour some users's messages
      If there's a match, strip out existing colour codes and put in our own
  """
  del(userdata) # shoosh, pylint
  # if the incoming message is ":nick!name@host PRIVMSG :message payload"
  # then word = ["nick","message payload"]
  nick = word[0]
  who = nick_to_fullname(nick)
  chan = xchat.get_info('channel')
  found_who = None
  for i in PEOPLE:
    if PEOPLE[i]['regexp'].match(who):
      if 'channel' in PEOPLE[i] :
        if chan in PEOPLE[i]['channel'] :
          found_who = i
          break
      else:
        found_who = i
        break
  if found_who:
    colour = PEOPLE[found_who]['colour']
    if isinstance(colour, int):
      colour = '\003%d' % colour
    elif colour in MIRC_COLOURS:
      colour = MIRC_COLOURS[colour]
    mesg = word_eol[1]
    # print('... firstchar %d lastchar %d' % (ord(mesg[0]), ord(mesg[-1])))
    if mesg.startswith(colour):
      # probably one of ours
      return xchat.EAT_NONE
    else:
      mesg = colour + MIRC_COLOUR_FIND.sub('', mesg.strip()) + MIRC_COLOUR_RESET
      xchat.emit_print("Channel Message", nick, mesg, '', nick_to_prefix(nick))
      return xchat.EAT_ALL
  return xchat.EAT_NONE

# -- main
for ccc in PEOPLE:
  PEOPLE[ccc]['regexp'] = ircglob_to_regexp(ccc)
  # print PEOPLE[ccc]['regexp'].pattern

xchat.hook_print('Channel Message', colour_someone)

print "loaded %s v%s" % (__module_name__, __module_version__)
#print "loaded %s v%s (no commands)" % (__module_name__, __module_version__)

