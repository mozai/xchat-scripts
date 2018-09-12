--[[
  this is a lua script for use with hexchat

  it's for figuring out how the hook_* stuff really
  works.  the hexchat lua document is pretty good
  but sometimes I want to watch the pistons fire.

  https://hexchat.readthedocs.io/en/latest/script_lua.html

  bad idea to leave this in ~/.hexchat/addons/
  better to use /lua load spew_test.lua then
  /lua unload spew_test.lua when you're done
]]

--[[ what to watch
  can we also use numeric events?
  and I don't know if lettercase matters
  bad idea to add "Key Press" to PRINT_EVENTS
]]
local _name, _version, _descr =
    'spew_test.lua', '20180911', 'Regurgitate what the hook_* stuff gets'
local SERVER_EVENTS = { 'PRIVMSG', 'NOTICE', 'PART', 'JOIN', 'KICK' }
local PRINT_EVENTS = { 'Channel Message', 'Channel Action', 'Your Message', 'Your Action' }


local dumps
dumps = function(i)
    if type(i) == 'table' then
        local s = '{ '
        for k,v in pairs(i) do
            if type(k) ~= 'number' then
                k = '"'..k..'"'
            end
            s = s .. '['..k..'] = ' .. dumps(v) .. ', '
        end
        return s .. '} '
    else
        return tostring(i)
    end
end


local hook_spew = function(word, eol, ...)
    print("*** " .. dumps(word))
    print("*** " .. dumps(eol))
    print("*** " .. dumps(...))
    return hexchat.EAT_NONE
end


if hexchat then
    print("Loading " .. _name .. "(/spew argle bargle)")
    hexchat.register(_name, _version, _descr)
    hexchat.hook_command('SPEW', hook_spew, 'regugitate parameters', hexchat.PRI_HIGHEST)
    for _,i in pairs(PRINT_EVENTS) do
        hexchat.hook_print(i, hook_spew, hexchat.PRI_HIGHEST)
    end
    for _,i in pairs(SERVER_EVENTS) do
        hexchat.hook_server(i, hook_spew, hexchat.PRI_HIGHEST)
    end
else
    print("This is a hexchat module; it's sensless to use it outside hexchat")
end

--[=[
  What I saw:

  /spew argle bargle =>
      *** { [1] = spew, [2] = argle, [3] = bargle,}
      *** { [1] = spew argle bargle, [2] = argle bargle, [3] = bargle,}
      *** nil

  I said "harble bargle dimple grimble" in a channel where I have ops =>
      *** { [1] = Mozai, [2] = argle bargle dimple grimble, [3] = @, }
      *** nil
      *** nil

  @kate said "do you ever get so full" =>
      *** { [1] = :kate!hex@<redacted>, [2] = PRIVMSG, [3] = #wetfish, [4] = :do, [5] = you, [6] = ever, [7] = get, [8] = so, [9] = full, }
      *** { [1] = :kate!hex@<redacted> PRIVMSG #wetfish :do you ever get so full, [2] = PRIVMSG #wetfish :do you ever get so full, [3] = #wetfish :do you ever get so full, [4] = :do you ever get so full, [5] = you ever get so full, [6] = ever get so full, [7] = get so full, [8] = so full, [9] = full, }
      *** nil
      *** { [1] = kate, [2] = do you ever get so full, [3] = @, }
      *** nil
      *** nil

  %Kitten emoted "Kitten  rubs her face against the door" =>
      *** { [1] = :Kitten!Kitten@<redacted>, [2] = PRIVMSG, [3] = #wetfish, [4] = :ACTION, [5] = rubs, [6] = her, [7] = face, [8] = against, [9] = the, [10] = door, }
      *** { [1] = :Kitten!Kitten@<redacted> PRIVMSG #wetfish :ACTION rubs her face against the door, [2] = PRIVMSG #wetfish :ACTION rubs her face against the door, [3] = #wetfish :ACTION rubs her face against the door, [4] = :ACTION rubs her face against the door, [5] = rubs her face against the door, [6] = her face against the door, [7] = face against the door, [8] = against the door, [9] = the door, [10] = door, }
      *** nil
      *** { [1] = Kitten, [2] = rubs her face against the door, [3] = %, }
      *** nil
      *** nil
]=]
