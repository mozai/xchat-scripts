#!/usr/bin/env lua
--[[ shake-the-eightball addon for Hexchat
    author: Moses Moore <moc.iazom@sesom>
    date: 2018-09-08

    config settings:
    TRIGGER: what to listen for
        matches start of string up to first whitespace
    TIMEOUT: seconds between responses, per-channel
    CHANNELS: which channels to listen for the command;
        special channel name '*' means "listen on all channels"
    ANSWERS: from the classic toy by Mattel; 10 yes, 5 no, 5 neutral
    NAMES: what to call myself i.e. "The Obsidian Oracle," "Vriska's fetish"
]]

--[[ CONFIG ]]
local TRIGGER = "!8ball"
local TIMEOUT = 15
local CHANNELS = {"#farts", "#wetfish", "#test", "#botspam"}
local ANSWERS = {
    'It is decidedly so', 'You may rely on it', 'Outlook good',
    'Yes definitely', 'Signs point to yes', 'Most likely',
    'Without a doubt', 'Yes', 'As I see it yes', 'It is certain',
    'Very doubtful', 'Outlook not so good', 'My sources say no',
    'Dont count on it', 'My reply is no', 'Better not tell you now',
    'Concentrate and ask again', 'Reply hazy try again',
    'Cannot predict now', 'Ask again later'
}
local NAMES = {
    'magic Eight-ball\u{2122}', '8ball', 'eightball', '\u{277d}'
}

--[[ INIT ]]
local LASTBLEAT = { }
for _, i in pairs(CHANNELS) do LASTBLEAT[i] = 0 end
--[[ 31607 is the largest prime <= sqrt(1e7) ]]
math.randomseed((os.time() + (os.clock() * 1e6)) % 31607)

local function random_choice(intable)
    local i, choice = 1, nil
    for k, _ in pairs(intable) do
        if math.random(i) == 1 then choice = k end
        i = i + 1
    end
    return intable[choice]
end

local function eightball_answer()
    return "The " .. random_choice(NAMES) .. " says: "
        .. "\x02" .. random_choice(ANSWERS) .. "\x02"
end

local function cmd_8ball(word, eol)
    print(eightball_answer())
end

local function msg_8ball(word, eol)
    local chan = hexchat.get_info("channel")
    if not (LASTBLEAT[chan] or LASTBLEAT['*']) then
        return hexchat.EAT_NONE
    end
    local cmd = word[2]:match("^%s*(%S*)")
    if not (cmd == TRIGGER) then
        return hexchat.EAT_NONE
    end
    if os.difftime(os.time(), LASTBLEAT[chan]) > TIMEOUT then
        LASTBLEAT[chan] = os.time()
        hexchat.command("say " .. eightball_answer())
    end
    return hexchat.EAT_PLUGIN
end

--[[ MAIN ]]
if hexchat then
    hexchat.register("eightball.lua",
        "shake the eightball (/8ball, " .. TRIGGER .. ")",
        "20180909"
    )
    hexchat.hook_print("Channel Message", msg_8ball)
    hexchat.hook_print("Your Message", msg_8ball)
    hexchat.hook_command("8BALL", cmd_8ball)
    print("8ball.lua : /8ball or " .. TRIGGER .. " in configured channels")
else
    cmd_8ball(nil, nil)
end