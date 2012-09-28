__module_name__  = "MOCP_info"
__module_version__  = "1"
__module_description__  = "MOCP Info Script"
__module_author__  =  "Mozai, kubicz10"

# Personalize this plugin by editing source code.
# I release this under terms of GPL license, http://www.gnu.org/copyleft/gpl.html

# Known commands:
# mocp         :displays current song information just to you
# mocp_emote   :announces song information to current channel
# mocp_full_info :'mocp' output spewed to current channel
# mocp_stop    :stops mocp from playing
# mocp_play    :start mocp
# mocp_next    :plays next song
# mocp_prev    :plays previous song
# mocp_toggle  :toggles between play and pause
# mocp_exit    :shutdown mocp.
import xchat
import commands

def _mocp_info():
  infodump = commands.getoutput("mocp -i")
  mocpinfo = dict()
  for line in str(infodump).split("\n"):
    fields = line.split(': ',2)
    mocpinfo[fields[0]] = fields[1].strip()
  return mocpinfo

def mocp_emote(word,word_eol,userdata):
  #Info Full#
  mocpinfo = _mocp_info()
  if (mocpinfo.has_key('State') and mocpinfo['State'] == "STOP"):
    print("mocp isnt running")
  else:
    blurb = ''
    for k in ('Artist','Album','SongTitle'):
      if (mocpinfo.has_key(k) and mocpinfo[k]):
        blurb += '%s - ' % mocpinfo[k]
    if blurb:
      blurb = blurb[:-3]
    elif (mocpinfo.has_key('SongTitle')):
      blurb += '%s' % mocpinfo['SongTitle']
    elif (mocpinfo.has_key('File')):
      blurb += '%s' % mocpinfo['File']
    if (blurb):
      xchat.command("me is listening to \002%s\002" % blurb)
    else:
      print("mocpinfo is empty? ( %s )" % str(mocpinfo))
  return xchat.EAT_ALL
xchat.hook_command("mocp_emote", mocp_emote, help="Announces MOCP info in current channel")

def mocp_full_info(word,word_eol,userdata):
  mocpinfo = _mocp_info()
  if (mocpinfo.has_key('State') and mocpinfo['State'] == "STOP"):
    print("mocp isnt running")
  if (mocpinfo.has_key('State') and mocpinfo['State'] == "STOP"):
    print("mocp isnt running")
  else:
    ks = mocpinfo.keys()
    if (len(ks) <= 0):
      print("mocpinfo is empty? ( %s )" % str(mocpinfo))
    else:
      ks.sort()
      blurb = ''
      for k in ks:
        if (mocpinfo[k]):
          blurb += "\002%s\002 %s " % (k,mocpinfo[k])
      xchat.command("me %s" % blurb)
  return xchat.EAT_ALL
xchat.hook_command("mocp_full_info", mocp_full_info, help="Spews MOCP info to channel")

def mocp_local_info(word,word_eol,userdata):
  #Info Local#
  mocpinfo = _mocp_info()
  if (mocpinfo.has_key('State') and mocpinfo['State'] == "STOP"):
    print("mocp isnt running")
  else:
    ks = mocpinfo.keys()
    if (len(ks) <= 0):
      print("mocpinfo is empty? ( %s )" % str(mocpinfo))
    else:
      ks.sort()
      blurb = ''
      for k in ks:
        if (mocpinfo[k]):
          blurb += "\002%s\002 %s " % (k,mocpinfo[k])
      print(blurb)
  return xchat.EAT_ALL
xchat.hook_command("mocp", mocp_local_info, help="Prints MOCP info")

def mocp_stop_playing(word,word_eol,userdata):
  #Stop playing#
  mocpinfo = _mocp_info()
  if (mocpinfo.has_key('State') and mocpinfo['State'] == "STOP"):
    print ("mocp is stoped or not running")
  else:
    commands.getoutput("mocp -s")
    print("stopping mocp")
  return xchat.EAT_ALL
xchat.hook_command("mocp_stop", mocp_stop_playing, help="Stop playing.")

def mocp_play(word,word_eol,userdata):
  #Start playing#
  mocpinfo = _mocp_info()
  if (mocpinfo.has_key('State') and mocpinfo['State'] == "PLAY"):
    print ("mocp is playing")
  else:
    commands.getoutput("mocp -p")
    print("mocp starts playing")
  return xchat.EAT_ALL
xchat.hook_command("mocp_play", mocp_play, help="Start playing from the first item on the playlist.")

def mocp_next(word,word_eol,userdata):
  #Next song#
  commands.getoutput("mocp -f")
  print("mocp jumps to next song")
  return xchat.EAT_ALL
xchat.hook_command("mocp_next", mocp_next, help="Play next song.")

def mocp_previous(word,word_eol,userdata):
  #Previous song#
  commands.getoutput("mocp -r")
  print("mocp jumps to previous song")
  return xchat.EAT_ALL
xchat.hook_command("mocp_prev", mocp_previous, help="Play previous song.")

def mocp_toggle(word,word_eol,userdata):
  #Toggle play/pause#
  mocpinfo = _mocp_info()
  if (mocpinfo.has_key('State') and mocpinfo['State'] == "PAUSE"):
    commands.getoutput("mocp -G")
    print("mocp unpaused")
  elif (mocpinfo.has_key('State') and mocpinfo['State'] == "PLAY"):
    commands.getoutput("mocp -G")
    print("mocp paused")
  else:
    print("mocp is stoped or isnt running")
  return xchat.EAT_ALL
xchat.hook_command("mocp_toggle", mocp_toggle, help="Toggle between play/pause.")

def mocp_exit(word,word_eol,userdata):
  #Exit mocp#
  commands.getoutput("mocp -x")
  print("mocp is off")
  return xchat.EAT_ALL
xchat.hook_command("mocp_exit", mocp_exit, help="Shutdown MOCP.")

print "XChat MOCP Info Script (python)"

