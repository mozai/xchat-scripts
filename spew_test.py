"""
  this is a python script for use with xchat v2.x.

  It is for figuring out how the hook_* stuff really
  works, because the xchatpython.html document
  has some awfully large holes in it.

  You should load this with `/py console` then
  `/py load spew_test.py` because you really
  don't want this to be automatically loaded up.

"""
# -- config, stuff the user will want to mess with

# server messages to hook_server() onto
#  doccos say you can do numerics too, but I don't know if it translates
#  the server messages properly, or if these are just substring matches and
#  thus I have to get the correct lettercase or numerics depending on the
#  server.
SERVER_EVENTS = ['PRIVMSG', 'NOTICE', 'PART', 'KICK']

# xchat print events to hook into
#   "The event names are available in the Edit Event Texts window."
#   except there IS NO SUCH THING.  In Xchat 2.8.8, go to the menubar
#   and look for Settings > Advanced... > Text Events...  First paramter
#   of xchat.hook_print() are the items in the left column, which you
#   have to guess each of their purposes (but its not difficult).
PRINT_EVENTS = [ ]


# -- init, stuff we do only once. No customer-servicable parts beyond here

__module_name__  = "spew_test"[:12]
__module_version__  = "20121108"[:8]
__module_description__  = "Regugitate what is received by hook_* stuff"[:32]
__module_author__  =  "Mozai <moc.iazom@sesom>"

import xchat

def hook_spew(word, word_eol, userdata):
  """ /analthread co/42546122 or
      /analthread http://boards.4chan.org/co/res/42546122
  """
  spew = { 'word' : word, 'word_eol': word_eol, 'userdata': userdata }
  print "*** " + repr(spew)
  return xchat.EAT_NONE


# -- main
print "\002Loading %s v%s\002" % (__module_name__, __module_version__)

xchat.hook_command('spew', hook_spew, help='regugitate parameters')
print "\002commands:\002 /spew [followed by nonsense data]"

for event in PRINT_EVENTS:
  xchat.hook_print(event, hook_spew)

for event in SERVER_EVENTS:
  xchat.hook_server(event, hook_spew)

# Things I saw that made xchat.hookserver() make more sense to me:
#"""  { 'word': [
#                ':Kyreen!~erh@amnet.net.au',
#                'PRIVMSG',
#                '#farts',
#                ':yeah',
#                'lets',
#                'party'
#               ],
#      'word_eol': [
#                   ':Kyreen!~erh@amnet.net.au PRIVMSG #farts :yeah lets party',
#                   'PRIVMSG #farts :yeah lets party',
#                   '#farts :yeah lets party',
#                   ':yeah lets party',
#                   'lets party',
#                   'party'
#                  ],
#    'userdata': None}
#"""
#""" :kazoo_!~kazoo@Rizon-73073BD1.fullrate.dk JOIN :#fart """
#""" :irc.thefear.ca PONG irc.thefear.ca :LAG791983761     """
#""" :kazoo!~kazoo@Rizon-73073BD1.fullrate.dk QUIT :Ping timeout: 240 seconds """

