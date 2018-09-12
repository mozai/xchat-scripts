#!/usr/bin/env lua
--[[
    get status of and control Clementine media player from inside hexchat
    Originally written in Python but hexchat + python + dbus would fail
    at best or wedge hexchat entirely at worse
    Clementine documentation says it uses MPRIS1 but it does not
]]
local _name, _version, _descr = "clementine.lua", "20180910", "Clementine (/clem help)"
local _mservice, _mpath = "org.mpris.MediaPlayer2", "/org/mpris/MediaPlayer2"

local _clem_qdbus = function(cmd)
    return "qdbus " .. _mservice .. ".clementine "
        .. _mpath .. " "
        .. _mservice .. ".Player." .. cmd
end

local cmd_clem = function(_, eol)
    local subcommand = eol[2]
    local res, emote, title, artist
    -- local album, url, length, position
    if (subcommand == 'help') or (subcommand == nil) then
        print("\x02/clem help\x02 this message")
        print("\x02/clem pause\x02 toggle playing")
        print("\x02/clem next\x02 go to next song")
        print("\x02/clem status\x02 what Clementine is doing")
        print("\x02/np\x02 utter current song's name in channel")
        return hexchat.EAT_PLUGIN
    elseif subcommand == 'pause' then
        --[[ prefer to 'stop' because paused livestreams act poorly on resume ]]
        res = io.popen(_clem_qdbus('PlaybackStatus')):read('a')
        if res == 'Playing' then
            os.execute(_clem_qdbus('Stop'))
        else
            os.execute(_clem_qdbus('Play'))
        end
    elseif subcommand == 'next' then
        os.execute(_clem_qdbus('Next'))
    elseif subcommand == 'status' then
        res = io.popen(_clem_qdbus('Metadata')):read('a')
        print(res)
    elseif subcommand == 'np' then
        res = io.popen(_clem_qdbus('PlaybackStatus')):read('a')
        if not (string.match(res, '%C*') == 'Playing') then
            print("Clementine is not playing (" .. res .. ")")
            return hexchat.EAT_PLUGIN
        else
            res = io.popen(_clem_qdbus('Metadata')):read('a')
            emote = "is listening to"
            title = string.match(res, 'xesam:title: (%C*)')
            if title then
                emote = emote .. " \x02" .. title .. "\x02"
            else
                emote = emote .. " music"
            end
            artist = string.match(res, 'xesam:artist: (%C*)')
            if artist then
                emote = emote .. " by " .. artist
            end
            --[[ album = string.match(res, 'xesam:album: (%C*)')
            length = string.match(res, 'mpris:length: (%C*)')
            url = string.match(res, 'xesam:url: (%C*)')
            if length then
                length = length / 1000000
                position = io.popen(_clem_qdbus('Position')) / 1000000
            end
            ]]
            hexchat.command("me " .. emote)
        end
    end
end

local cmd_np = function(_, _)
    cmd_clem({'clem', 'np'}, {'clem np', 'np'})
end

if hexchat then
    hexchat.register(_name, _version, _descr)
    hexchat.hook_command("CLEM", cmd_clem)
    hexchat.hook_command("NP", cmd_np)
    print("\x02" .. _name .. "\x02 " .. _descr)
else
    print("This is a hexchat module; test output below\n-----")
    cmd_clem({'clem', 'status'}, {'clem status', 'status'})
end
