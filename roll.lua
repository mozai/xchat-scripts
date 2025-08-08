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
    local i,j,ii,jj,pool,answer
    --[[ TODO: Greg Stolze's One-Roll Engine (ORE) ]]
    --[[ roll Xd10, keep matching sets, wide = strong, high = accurate ) ]]
    pool = {}
    if what:match("^%d+ore%d*$") then
      i,j = what:match("^(%d+)ore(%d*)")
    elseif what:match("^%d+ORE%d*$") then
      i,j = what:match("^(%d+)ORE(%d*)")
    end
    i = tonumber(i) or 6
    j = tonumber(j) or 10
    if j > 63 then j = 64 end
    if i > j then i = j end
    answer = "rolling " .. i .. "d" .. j .." ORE "
    for ii=1,i,1 do
      jj = math.random(j)
      pool[jj] = (pool[jj] or 0) + 1
    end
    matches = {}
    for i,j in pairs(pool) do
      table.insert(matches, j .. "x" .. i)
    end
    table.sort(matches, function(a,b) return a > b end) 
    answer = answer .. "(" .. table.concat(matches, ",") .. ")"
    return answer
end

local function rollFudge(what)
    local i,j,k,ii,jj,answer
    --[[ fudge dice: 4d3 (-,o,+) summed. ]]
    --[[ almost but not quite the same as d6-d6 ]]
    i = 4
    j = 0
    k = 0
    if what:match("^%d+[dD]F") then
      i = tonumber(what:match("^(%d+)[dD]F"))
    end
    if i > 64 then i = 64 end
    answer = "rolling " .. i .. "dF ("
    ii = 0
    while (ii < i) do
      jj = math.random(3)
      if (jj == 1) then
        j = j - 1
        answer = answer .. "-"
      elseif (jj == 2) then
        answer = answer .. "o"
      elseif (jj == 3) then
        k = k + 1
        answer = answer .. "+"
      end
      ii = ii + 1
    end
    answer =  answer .. ") " .. (j + k)
    return answer
end


local function rollPolyhedra(what)
    local i,j,k,ii,answer
    i = 2 j = 6 k = 0 --[[ default 2d6+0 ]]
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
    else
      --[[ rachel would do "!roll jizz" ]]
      return nil
    end
    i = tonumber(i) or 0
    j = tonumber(j) or 0
    k = tonumber(k) or 0
    if i > 63 then i = 64 end
    if j > 65535 then j = 65535 end
    if k > 65535 then k = 65535 end
    if k > 0 then
        answer = "rolling " .. i .. "d" .. j .. "+" .. k .. " ("
    elseif k < 0 then
        answer = "rolling " .. i .. "d" .. j .. "-" .. k .. " ("
    else
        answer = "rolling " .. i .. "d" .. j .. " ("
    end
    sum = 0
    if (i > 0 and j > 0) then
      ii = 0
      while (ii < i) do
        jj = math.random(j)
        answer = answer .. jj
        if (ii < i-1) then answer = answer .. "," end
        sum = sum + jj
        ii = ii + 1
      end
      answer = answer .. ")"
      if (k > 0) then
        answer = answer .. "+" .. k
        sum = sum + k
      elseif (k < 0) then
        answer = answer .. k
        sum = sum + k
      end
      answer = answer .. " " .. sum
    end
    return answer
end

local function roll(what)
    if what:match("^%d+ore%d*") then
      --[[ pool of five d10 == 5ore or 5ore10 ]]
      return rollORE(what)
    elseif what:match("^%d+ORE%d*$") then
      return rollORE(what)
    elseif what:match("^%d+[dD]F$") then
      return rollFudge(what)
    else
      return rollPolyhedra(what)
    end
end

local function cmd_roll(word, eol)
    local what
    what = "2d6"
    if word and word[2] then
        if word[2]:match("%d*[dD]%d+") then
            what = word[2]
        elseif word[2]:match("%d*[dD]F") then
            what = word[2]
        elseif word[2]:match("%d+ore%d*") then
            what = word[2]
        elseif word[2]:match("%d+ORE%d*") then
            what = word[2]
        end
    end
    print(roll(what))
end

local function msg_roll(word, eol)
    local chan = hexchat.get_info("channel")
    local answer
    if not (LASTROLL[chan] or LASTROLL['*']) then return hexchat.EAT_NONE end
    local cmd = word[2]:match("^%s*(%S+)")
    if not (cmd == TRIGGER) then return hexchat.EAT_NONE end
    local what = word[2]:match("^%s*%S+%s+(%S+)")
    if not (what) then what = "2d6" print("using default 2d6") end
    if os.difftime(os.time(), LASTROLL[chan]) > TIMEOUT then
        answer = roll(what)
        if not (answer == nil) then
            hexchat.command("me " .. answer)
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
    testcmd = {"roll", "3d6"}
    print("Testing, ten rolls of " .. testcmd[2])
    while ii < 10 do
        cmd_roll(testcmd, nil)
        ii = ii + 1
    end
end

