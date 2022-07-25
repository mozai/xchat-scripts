#!/usr/bin/env lua
--[[ roll the dice
    author: Moses Moore <moc.iazom@sesom>
    date: 2019-09-01
    because I had a python module but the embedded python interpreter
    in hexchat keeps crashing and taking the rest of hexchat with it

    config settings:
    CHANNELS: which channels to listen for the command;
        special channel name '*' means "listen on all channels"
    TIMEOUT: seconds between responses, per-channel
    TRIGGER: what to listen for
        matches start of string up to first whitespace
]]
--[[ IDEA: draw a bridge/poker card, or tarrochi card, but keep state
           of the deck of cards so you won't pull the same one until all
           else were pulled, or someone says "shuffle" ]]

--[[ CONFIG ]]

local CHANNELS = {"#farts", "#wetfish", "#test", "#botspam"}
local TIMEOUT = 2
local TRIGGER = "!roll"

--[[ INIT ]]

local LASTROLL = { }
for _,i in pairs(CHANNELS) do LASTROLL[i] = 0 end
math.randomseed((os.time() + (os.clock() * 1e6)) % 31612)

local function rollORE(what)
    local i,j,answer
    --[[ TODO: Greg Stolze's One-Roll Engine (ORE) ]]
    --[[ roll Xd10, keep matching sets, wide = strong, high = accurate ) ]]
    i = 6
    j = 10
    answer = "(not implemented yet)"
    return answer
end

local function rollFudge(what)
    local i,j,k,ii,jj,answer
    --[[ fudge dice: 4d3 (-,o,+) summed. ]]
    --[[ almost but not quite the same as d6-d6 ]]
    i = 4
    j = 0
    k = 0
    if what:match("^%d+[dD]F$") then
      i = what:match("^(%d+)[dD]F")
    end
    answer = "rolling " .. i .. "dF ("
    ii = 0
    while (ii < i) do
      jj = math.random(3)
      if (jj == 1) then
        j = j - 1
        answer = answer .. "-"
      elseif (jj == 2) then
        answer = answer .. "·"
      elseif (jj == 3) then
        k = k + 1
        answer = answer .. "+"
      end
    end
    answer =  answer .. ") " .. (j + k)
    return answer
end


local function roll(what)
    local i,j,k,answer
    i = 2 j = 6 k = 0 --[[ default 2d6+0 ]]
    if what:match("^ore%d([dD]%d)?$") then
      --[[ pool of five d10 == ore5 or ore5d10 ]]
      return rollORE(what)
    elseif what:match("^%d[dD]F$") then
      return rollFudge(what)
    elseif what:match("^%d[dD]F$") then
      return rollFudge(what)
    end
    if what:match("^%d+[dD]%d+[+-]%d+$") then
      i,j,k = what:match("^(%d+)[dD](%d+)([-+]%d+)")
    elseif what:match("^%d+[dD]%d+$") then
      i,j = what:match("^(%d+)[dD](%d+)")
      k = 0
    elseif what:match("^[dD]%d+[-+]%d+$") then
      i = 1
      j,k = what:match("^[dD](%d+)([-+]%d+)")
    elseif what:match("^[dD]?%d+$") then
      i = 1
      j = what:match("^[dD]?(%d+)")
      k = 0
    end
    if i then
      answer = 0
      ii = 0
      i = i + 0
      while (ii < i) do
        answer = answer + math.random(j)
        ii = ii + 1
      end
      answer = answer + k
      return answer
    end
    return answer
end

local function cmd_roll(word, eol)
    local what
    if word then
        what = word[1]:match("^%s*%S+%s+(%S+)")
    end
    if not what then
        what = "2d6"
    end
    print("rolled " .. roll(what))
end

local function msg_roll(word, eol)
    local chan = hexchat.get_info("channel")
    local answer
    if not (LASTROLL[chan] or LASTROLL['*']) then return hexchat.EAT_NONE end
    local cmd = word[2]:match("^%s*(%S+)")
    if not (cmd == TRIGGER) then return hexchat.EAT_NONE end
    local what = word[2]:match("^%s*%S+%s+(%S+)")
    if not (what) then what = "2d6" end
    if os.difftime(os.time(), LASTROLL[chan]) > TIMEOUT then
        answer = roll(what)
        if not (answer == nil) then
            hexchat.command("me rolled " .. answer)
            LASTROLL[chan] = os.time()
        end
    end
    return hexchat.EAT_PLUGIN
end

--[[ MAIN ]]

if hexchat then
    hexchat.register(
        "roll.lua",
        "20220725",
        "roll them bones (/roll, /roll 3d6, " .. TRIGGER .. ")"
    )
    hexchat.hook_print("Channel Message", msg_roll)
    hexchat.hook_print("Your Message", msg_roll)
    hexchat.hook_command("ROLL", cmd_roll)
    print("roll.lua : /roll or " .. TRIGGER .. " in configured channels")
else
    local ii = 0
    print("Testing, ten rolls of 2d6")
    while ii < 10 do
        cmd_roll(nil, nil)
        ii = ii + 1
    end
end

