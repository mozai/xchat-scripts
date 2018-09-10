#!/usr/bin/env lua
--[[
    gaypride
    Hexchat module to utter something F*A*B*U*L*O*U*S
    author: Moses Moore <moc.iazom@sesom>
]]

local RAINBOW = {
  '\x0304', '\x0305', '\x0308', '\x0309', '\x0303',
  '\x0312', '\x0302', '\x0313', '\x0306'
}

local function cmd_gaypride(word, eol)
    local phrase, pride = eol[2], ''
    local crumbsize = math.ceil(#phrase / #RAINBOW)
    local i = 0
    while i < #RAINBOW do
        pride = pride .. RAINBOW[i+1] .. string.sub(phrase, (i*crumbsize)+1, ((i+1)*crumbsize))
        i = i + 1
    end
    hexchat.command("say " .. pride)
end

--[[ MAIN ]]
if hexchat then
    hexchat.register("gaypride.lua",
        "rainbow flag (/gay <message>)",
        "20180909"
    )
    hexchat.hook_command("GAY", cmd_gaypride)
    hexchat.hook_command("PRIDE", cmd_gaypride)
    print("gaypride.lua : /pride <message>")
else
    print("this is a hexchat module; doesn't work outside of hexchat")
end