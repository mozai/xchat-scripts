"""
  this is a python script for use with hexchat v2.x.

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
PRINT_EVENTS = [ 'Channel Message', 'Channel Action', 'Your Message', 'Your Action' ]


# -- init, stuff we do only once. No customer-servicable parts beyond here

__module_name__  = "spew_test"[:12]
__module_version__  = "20121108"[:8]
__module_description__  = "Regugitate what is received by hook_* stuff"[:32]
__module_author__  =  "Mozai <moc.iazom@sesom>"

import hexchat
import json

def hook_spew(word, word_eol, userdata):
  """ /analthread co/42546122 or
      /analthread http://boards.4chan.org/co/res/42546122
  """
  spew = { 'word' : word, 'word_eol': word_eol, 'userdata': userdata }
  print("*** " + json.dumps(spew))
  return hexchat.EAT_NONE


# -- main
print("\002Loading %s v%s\002" % (__module_name__, __module_version__))

hexchat.hook_command('spew', hook_spew, help='regugitate parameters')
print("\002commands:\002 /spew [followed by nonsense data]")

for event in PRINT_EVENTS:
  hexchat.hook_print(event, hook_spew, userdata={'event': event})

for event in SERVER_EVENTS:
  hexchat.hook_server(event, hook_spew, userdata={'event': event})

# things I saw:
# { "userdata": {"event": "Your Message"},
#   "word": ["Mozai", "!8ball am I pretty?", "@"],
#   "word_eol": ["Mozai !8ball am I pretty? @", "!8ball am I pretty? @", "@"] }
#
# *** {
#   "word": [":kate!hexafluorid@Fish-18io58.s.time4vps.cloud", "PRIVMSG", "#wetfish", ":not", "years", "at", "least"],
#   "word_eol": [":kate!hexafluorid@Fish-18io58.s.time4vps.cloud PRIVMSG #wetfish :not years at least", "PRIVMSG #wetfish :not years at least", "#wetfish :not years at least", ":not years at least", "years at least", "at least", "least"],
#   "userdata": {"event": "PRIVMSG"} }
# *** {
#   "word": ["kate", "not years at least"],
#   "word_eol": ["kate not years at least", "not years at least"],
#   "userdata": {"event": "Channel Message"} }
