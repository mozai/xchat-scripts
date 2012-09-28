Scripts as plugins for XChat 2
==============================

Been spending a lotta time with [XChat 2](http://xchat.org/) running on
my desktop.  I thought I'd add some features, since it has a module
for loading python/ perl/ tcl scripts that can latch on to hooks in
the software.   Also, I need to keep practicing.

grubdate\_xchat.py
---------------------
Adds commands to check websites for the age of the most recent update.
Originaly meant for 'mspaintadventures.com', where "grubdate" would be
an in-joke.  It now uses a configuration file for multiple websites.

It also has a feature where people in a prescribed set of channels can
utter a '!blah' or '.blah' message to request this command.  It has
timeout features to prevent abusing this to spam a channel.

*TODO: a search regexp in case the latest update has a diff path each time.*

mocp\_xchat.py
--------------
A large improvement of the original MOCP\_info script by kubicz10 (released
under a GNU copyleft license).  I might rewrite it from scratch soon,
but kubicz10 deserves props for doing it first.

MOC ("Music On Console") is an audio-file player that uses a client-daemon
architecture, so you can quit the client without stopping the media queue
playback.  You can either give the daemon single commands at a terminal
prompt, or start the ncurses interface ('mocp') that comes with.

This script adds commands to XChat to control MOC with XChat commands, so
you do not need to leave your IRC session.  You can also (discretely) 
emit to yourself or the current channel what you are currently listening to.

madlibs\_xchat.py
-----------------
Coming soon.  This will be an interface for using my 
[madlibs python module](http://github.com/mozai/python-madlibs) 
to emit random phrases and edit vocabulary datasets within XChat.
