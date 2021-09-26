#!/usr/bin/env lua
--[[ cantrips
    author: Moses Moore <moc.iazom@sesom>
    date: 2021-04-11

    originally I wanted something in lua that would fetch a url
    and parse what it gets, but the "lua-http" package for Ubuntu
    is broken[^1], and the "luarocks install http" doesnt work either
    [1: https://bugs.launchpad.net/ubuntu/+source/lua-http/+bug/1792052]
    So I'll just do a generic "launch a program and bark the first line"

    config settings:
    CHANNELS: which channels to listen for the command;
        special channel name '*' means "listen on all channels"
    TIMEOUT: seconds between responses, all channels
    CANTRIPS: a table of cantrip tables.
    cantrip[trigger]: what to listen for in the channel; throttled by TIMEOUT
    cantrip[cmd]: what /command will trigger this cantrip
    cantrip[help]: what to say if a human asks for guidance
    cantrip[spell]: what to give `/bin/sh -c` to get the first line
      truncated to first occurance of '\n' or 440 characters.

]]

--[[ CONFIG ]]

local CHANNELS = {"#farts", "#wetfish", "#test", "#botspam"}
local TIMEOUT = 15
local CANTRIPS = {
  { trigger = "!fortune",
    cmd = "fortune",
    help = "gives a fortune cookie",
    --[[ spell = "/usr/bin/fortune -s" }, ]]
    spell = "/usr/bin/fortune -n240 -s local |fmt -w240", },
  { trigger = "!ud",
    cmd = "ud",
    help = "fetches a definition from UrbanDictionary",
    spell = "/usr/bin/wget -qO- 'https://www.urbandictionary.com/define.php?term={}' |/usr/bin/xmllint 2>/dev/null --nonet --html --nowrap --xpath 'string(//meta[@property=\"og:description\"]/@content)' -", },
  { trigger = "!dadjoke",
    cmd = "dadjoke",
    help = "utter a dad-joke (fortune cookie)",
    spell = "/usr/bin/fortune -n240 -s dadjokes |fmt -w240", },
}

--[[ INIT ]]

local posix = require "posix"  
local LASTBARK = { }
for _,i in pairs(CHANNELS) do LASTBARK[i] = 0 end

--[[
TODO: io.popen():read() will block hexchat!
  anything that depends on internet i/o can lock up 
  the entire hexchat program for 5-30 seconds
  `io.popen("string to launch in subshell") is undocumented and not universal
  local Hnd, ErrStr = io.popen("ls -la")
  if Hnd then
    for Line in Hnd:lines() do
      print(Line)
    end
    Hnd:close()
  else
    print(ErrStr)
  end
  see http://lua-users.org/lists/lua-l/2016-04/msg00019.html for how
  to do this using coroutines and system select() calls
]]
  

local function _cast_spell(cmd, param)
  local ph,err,answer
  if string.find(cmd, '{}') then
    param = param or ''
    param = string.gsub(param, '\x0A', ' ')
    --[[ make sure the cmd string safe ]]
    if string.find(param, "[!&#%;`|*?~<>^(){}$\\\x0A\x5b\x5c\xFF]") then
      print("refusing to execute with bad param `" .. param .. "`")
      return nil
    end
    cmd = string.gsub(cmd, '{}', param)
  end
  --[[ thin wrapper around "/bin/sh -c" ]]
  --[[ may block;  see above for guesses sur comment faire sans bloque ]]
  ph, err = io.popen(cmd)
  if ph then
    answer = ph:read("l") -- [[ only want first line ]]
    ph:close()
    return answer
  else
    print(err)
  end
end

local function cmd_cantrip(word, eol)
  --[[ "/thumblr tavros ntriam" ->
       word = { "thumblr", "tavros", "nitram" }
       eol = { "thumblr tavros nitram", "tavros nitram", "nitram" }
  ]]
  local i, cantrip, param, answer
  for _,i in pairs(CANTRIPS) do
    if word[1] == i.cmd then
      cantrip = i
      break
    end
  end
  if cantrip and cantrip.spell then
    --[[ print("\x02\x0302" .. "spell:\x0F " .. cantrip.spell .. " " .. (eol[2] or '')) ]]
    answer = _cast_spell(cantrip.spell, eol[2])
    if answer then
      hexchat.command("say " .. answer)
      --[[ print(answer) ]]
    end
  end
end

local function msg_cantrip(word, eol)
  local answer, cantrip, chan, cmd, what
  chan = hexchat.get_info("channel")
  if not (LASTBARK[chan] or LASTBARK['*']) then return hexchat.EAT_NONE end
  trigger, extras = word[2]:match("^%s*(%S+)%s*([A-Za-z0-9]*)")
  for _,i in pairs(CANTRIPS) do
    if (trigger == i.trigger) then
      cantrip = i
      break
    end
  end
  if cantrip then
    if (os.difftime(os.time(), LASTBARK[chan]) <= TIMEOUT) then
      return hexchat.EAT_NONE
    end
    --[[ Zhu Li! do the thing! ]]
    answer = _cast_spell(cantrip.spell, extras)
    if answer then
      hexchat.command("say " .. answer)
      LASTBARK[chan] = os.time()
    end
    return hexchat.EAT_PLUGIN
  end
  return hexchat.EAT_NONE
end

--[[ MAIN ]]

local function usage()
  for _,i in pairs(CANTRIPS) do
    print("- /" .. i.cmd .. " " .. i.trigger .. "\n  " .. i.help)
  end
end
 
if hexchat then
    hexchat.register( "cantrips.lua", "20210411",
      "just lua invoking little one-line-output commands"
    )
    hexchat.hook_print("Channel Message", msg_cantrip)
    hexchat.hook_print("Your Message", msg_cantrip)
    for _,i in pairs(CANTRIPS) do
        if i.cmd then  
            hexchat.hook_command(i.cmd, cmd_cantrip, i.help)
        end
    end
    usage()
else
  --[[ test mode ]]
  usage()
  hexchat = {}
  hexchat.command = print
  print("Casting the fortune cantrip")
  cmd_cantrip({"fortune"}, {"fortune"})
end

