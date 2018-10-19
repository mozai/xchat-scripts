#!/usr/bin/env lua
--[[
    get status of and control Music On Console (MOC) audio player
    Originally written in Python but I already rewrote the Clementine
    addon in Lua so wine knot
]]
--[[ "alexa play a lullaby" 
     ɴᴏᴡ ᴘʟᴀʏɪɴɢ: Friday I'm In Love | The Cure | Wish
     ─────────⚪───── ◄◄⠀▶⠀►►⠀ 00:25 / 00:39  ───○ 🔊 ᴴᴰ ⚙️ 
]]

local _name, _version, _descr = "mocp.lua", "20181017", "Music On Console (/mocp help)"

local _moc_status = function()
    local proc, line, answer, i
    p = io.popen("mocp --info")
    answer = { }
    for line in p:lines() do
        i = line:find(": ")
        if i ~= nil then
            answer[line:sub(1, i-1)] = line:sub(i+2)
        end
    end
    p:close()
    if answer["FATAL_ERROR"] ~= nil then
        answer = nil
    elseif answer.State == nil then
        answer = nil
    end
    return answer
end

local cmd_mocp = function(_, eol)
    local subcommand = eol[2]
    local emote, i, j
    status = _moc_status()
    if subcommand == 'np' then
        if status == nil then
            --[[ MOC not found or not running
                 let "/np" pass so something else can answer
            ]]
            return hexchat.EAT_NONE
        elseif status.State == 'PLAY' then
            emote = "is listening to "
            if status.SongTitle ~= nil then
                emote = emote .. "\x02" .. status.SongTitle .. "\x02 "
            elseif (status.Artist ~= nil) or (status.Album ~= nil) then
                emote = emote .. "something "
            end
            if status.Artist ~= nil then
                emote = emote .. "by " .. status.Artist .. " "
            end
            if status.Album ~= nil then
                emote = emote .. "from \"" .. status.Album .. "\" "
            end
            hexchat.command("me " .. emote)
        else
            print("MOC is not playing (" .. status.State .. ")")
        end
    elseif (subcommand == 'help') or (subcommand == nil) then
        print("\x02/mocp help\x02 this message")
        print("\x02/mocp pause|play|stop\x02 control playing")
        print("\x02/mocp next\x02 go to next song")
        print("\x02/mocp status\x02 what MOC is doing")
        print("\x02/np\x02 utter current song's name in channel")
    elseif (status == nil) then
        print("MOC not detected or isn't running")
    elseif subcommand == 'pause' then
        if status.State == "PAUSE" then
            os.execute("mocp --unpause")
        elseif status.State == "PLAY" and status.File.Sub(1, 4) == "http" then
            --[[ streams act poorly on pause->resume ]]
            os.execute("mocp --stop")
        elseif status.State == "PLAY" then
            os.execute("mocp --pause")
        else
            os.execute("mocp --play")
        end
    elseif subcommand == 'play' then
        if status.State ~= "PLAY" then
            os.execute("mocp --play")
        end
    elseif subcommand == 'stop' then
        if status.State ~= "STOP" then
            os.execute("mocp --stop")
        end
    elseif subcommand == 'next' then
        if status.State ~= "PLAY" then
            print "MOC not playing"
        else
            os.execute("mocp --next")
        end
    elseif subcommand == 'status' then
        for i, j in pairs(status) do
            print(":" .. i .. ": " .. j)
        end
    else
        return hexchat.EAT_NONE
    end
    return hexchat.EAT_PLUGIN
end

local cmd_np = function(_, _)
    cmd_mocp({'mocp', 'np'}, {'mocp np', 'np'})
end

if hexchat then
    hexchat.register(_name, _version, _descr)
    hexchat.hook_command("MOCP", cmd_mocp)
    hexchat.hook_command("NP", cmd_np)
    print("\x02" .. _name .. "\x02 " .. _descr)
else
    hexchat = { ["EAT_PLUGIN"]=nil }
    print("This is a hexchat module; test output below\n-----")
    cmd_mocp({'mocp', 'status'}, {'mocp status', 'status'})
end
