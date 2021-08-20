#!/usr/bin/env lua
--[[
    get status of and control Clementine media player from inside hexchat
    Originally written in Python but hexchat + python + dbus would fail
    at best or wedge hexchat entirely at worse
    Clementine documentation says it uses MPRIS1 but it does not
]]
--[[ "alexa play a lullaby" 
     ɴᴏᴡ ᴘʟᴀʏɪɴɢ: Friday I'm In Love | The Cure | Wish
     ─────────⚪───── ◄◄⠀▶⠀►►⠀ 00:25 / 00:39  ───○ 🔊 ᴴᴰ ⚙️ 
]]
--[[ on Ubuntu, it's not enough to install 'qdbus' you must 
     'sudo apt install qtdbus-qt5'
     Why do I have to install all th Qt5 libraries?  augh.
     going to use systemd's busctl instead
]]
--[[ Cant use the "media_player" luarock because 
     Failed installing dependency: https://luarocks.org/lgi-0.9.2-1.src.rock
      error: too few arguments to function ‘lua_resume’
]]

local _name, _version, _descr = "clementine.lua", "20180910", "Clementine (/clem help)"

local _clem_get = function(property)
    --[[ a{sv} 4 "mpris:trackid" s "/org/clementineplayer/Clementine/Track/41" "xesam:artist" as 1 "Telex" "xesam:title" s "Peanuts" "xesam:url" s "http://ice2.somafm.com/u80s-128-mp3" ]]
    local p = io.popen("busctl 2>&1 --user -- get-property org.mpris.MediaPlayer2.clementine /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player " .. property)
    if p ~= nil then return p:read('a') else return nil end
end
--[[ use this to find out what you can get out of Clementine
     busctl --user call org.mpris.MediaPlayer2.clementine /org/mpris/MediaPlayer2 org.freedesktop.DBus.Introspectable Introspect --verbose
]]
local _clem_cmd = function(method)
    --[[ busctl --user call org.mpris.MediaPlayer2.clementine /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player org.freedesktop.MediaPlayer2.Pause ]]
    local p = io.popen("busctl 2>&1 --user -- call org.mpris.MediaPlayer2.clementine /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player " .. method)
end

local _clem_playbackstatus = function()
    --[[ busctl --user get-property org.mpris.MediaPlayer2.clementine /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player PlaybackStatus
       s "Playing" | s "Stopped" | Failed to get property
    ]]
    local i = _clem_get("PlaybackStatus")
    return i:match("^s \"([^\"]+)\"")
end

local _clem_metadata_cook = function()
    --[[ a{sv} 4 "mpris:trackid" s "/org/clementineplayer/Clementine/Track/41" "xesam:artist" as 1 "Telex" "xesam:title" s "Peanuts" "xesam:url" s "http://ice2.somafm.com/u80s-128-mp3" ]]
    local retval={}
    local res = _clem_get('Metadata')
    if res == nil then return retval end
    --[[ the \" -> BEL trick is dirty but should work ]]
    res = res:gsub('\\"','\a')
    retval.title = string.match(res, '"xesam:title" s "([^"]*)"')
    if retval.title then retval.title = retval.title:gsub('\a', '"') end
    retval.artist = string.match(res, '"xesam:artist" as %d "([^"]*)"')
    if retval.artist then retval.artist = retval.artist:gsub('\a', '"') end
    retval.album = string.match(res, '"xesam:album" s "([^"]*)"')
    if retval.album then retval.album = retval.album:gsub('\a', '"') end
    --[[
    length = string.match(res, 'mpris:length: (%C*)')
    url = string.match(res, 'xesam:url: (%C*)')
    if length then
        length = length / 1000000
        position = _clem_get('Position')) / 1000000
    end
    ]]
    return retval
end

local cmd_clem = function(_, eol)
    --[[ $1 -> { 1: "clem", 2: "play", 3: "Lena, 4: "Raine" }
         $2 -> { 1: "clem play Lena Raine", 2: "play Lena Raine", 3: "Lena Raine", 4: "Raine" }
    ]]
    local subcommand = eol[2]
    local res, emote, title, artist, clemstatus
    -- local album, url, length, position
    clemstatus = _clem_playbackstatus()
    if subcommand == 'np' then
        if clemstatus == nil then
            --[[ Clementine not running but don't eat "/np" just in case ]]
            return hexchat.EAT_NONE
        elseif clemstatus == 'Playing' then
            res = _clem_metadata_cook()
            emote = "is listening to"
            if res.title then
                emote = emote .. " \x02" .. res.title .. "\x02"
            else
                emote = emote .. " music"
            end
            if res.artist then emote = emote .. " by " .. res.artist end
            --[[ if res.album then emote = emote .. " on \"" .. res.album .. "\"" ]]
            hexchat.command("me " .. emote)
        else
            print("Clementine is not playing (" .. clemstatus .. ")")
        end

    elseif (subcommand == 'help') or (subcommand == nil) then
        print("\x02/clem help\x02 this message")
        print("\x02/clem next|pause|play|rewind|stop\x02 control playing")
        print("\x02/clem status\x02 what is Clementine doing")
        print("\x02/np\x02 utter current song's name in channel")

    elseif (clemstatus == nil) then
        --[[ all the following subcommands need Clementine ]]
        print("Clementine not detected")

    elseif subcommand == 'pause' then
        --[[ prefer to 'stop' because paused livestreams act poorly on resume ]]
        if clemstatus == 'Playing' then
            _clem_cmd('Stop')
        else
            _clem_cmd('Play')
        end
    elseif subcommand == 'play' then
        _clem_cmd('Play')
    elseif subcommand == 'next' then
        _clem_cmd('Next')
    elseif subcommand == 'rewind' then
        --[[ seek ahead negative one hour's worth of microseconds ]]
        _clem_cmd('Seek x -3600000000')  
    elseif subcommand == 'stop' then
        _clem_cmd('Stop')
    elseif subcommand == 'status' then
        print(_clem_get('Metadata'))
    else
        return hexchat.EAT_NONE
    end
    return hexchat.EAT_PLUGIN
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
    hexchat = {}
    print("This is a hexchat module; test output below\n-----")
    cmd_clem({'clem', 'status'}, {'clem status', 'status'})
end
