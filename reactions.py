import discord
import asyncio
import json
import random
import emoji

client = discord.Client()


@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    user_load()
    roles_load()


@client.event
@asyncio.coroutine
def on_message(message):
    # print(message.content)
    if message.author.server_permissions.administrator:
        if message.content.startswith('!start'):
            yield from start(message)
        if message.content.startswith('!roles'):
            yield from roles(message, True)
        if message.content.startswith('!addrole'):
            yield from add_role(message)
        if message.content.startswith('!poll'):
            yield from new_poll(message)
    if message.content.startswith('!reg'):
        contains_emoji = False
        for i in message.content:
            if char_is_emoji(i):
                contains_emoji = True
                # yield from add_reaction(message, i)
                yield from register(message.author, message.channel, i)
        if not contains_emoji:
            yield from send_message(message.channel,
                                    message.author.mention + " Deine Nachricht enthält kein gültiges Emoji!")


def user_load():  # Load userdata
    global gl_users
    try:
        with open("user.json", "r") as file:
            gl_users = json.loads(file.read())
    except:
        print("Keine Benutzerdatenbank gefunden. Benutzerdatenbank wird erstellt.")
        with open("user.json", "w") as file:
            gl_users = {}


def roles_load():
    global gl_roles
    try:
        with open("roles.json", "r") as file:
            gl_roles = json.loads(file.read())
    except:
        print("Keine Rollendatenbank gefunden. Rollendatenbank wird erstellt.")
        with open("roles.json", "w") as file:
            gl_roles = {}


def char_is_emoji(character):
    return character in emoji.UNICODE_EMOJI


@asyncio.coroutine
def start(message):
    global gl_users
    global gl_roles
    user_arr = []
    for user in gl_users:
        user_arr.append(user)
    random.shuffle(user_arr)
    i = 0
    for role in gl_roles:
        for i2 in range(0, gl_roles[role][0]["argument"]):
            gl_roles[role][0]["user"].append(user_arr[i])
            gl_users[user_arr[i]][0]["role"].append(role)
            i = i + 1
    dump_array('user.json', gl_users)
    dump_array('roles.json', gl_roles)
    content = "Das Spiel wurde gestartet! Folgende Rollen sind im Spiel:\n"
    yield from send_message(message.channel, content)
    yield from roles(message, False)


@asyncio.coroutine
def roles(message, admin):
    global gl_users
    global gl_roles
    arguments = message.content.split()
    bol = False
    if len(arguments) > 1:
        if admin and arguments[1] == '-u':
            bol = True
    content = "**Rollen im Spiel:**\n\n"
    for role in gl_roles:
        content += "*" + role + "* "
        if bol:
            content += ": "
            for user in gl_roles[role][0]['user']:
                content += gl_users[user][0]['name'] + " "
        content += "\n"
    yield from send_message(message.channel, content)


@asyncio.coroutine
def add_role(message):
    global gl_roles
    arguments = message.content.split()
    gl_roles[arguments[1]] = [{"user": [], "argument": int(arguments[2])}]
    dump_array("roles.json", gl_roles)
    yield from send_message(message.channel, "Die Rolle \"" + arguments[1] + "\" wurde hinzugefügt")


@asyncio.coroutine
def register(user, channel, emoji):
    global gl_users
    for cur_user in gl_users:  # Userdatenbank durchsuchen
        # print(user)
        if user.id == cur_user:
            content = user.mention + " Du bist schon dabei!"
            yield from send_message(channel, content)
            return

    gl_users[user.id] = [{"name": user.name, "discriminator": user.discriminator,
                          "emoji": emoji, "mention": user.mention, "role": []}]

    dump_array("user.json", gl_users)
    content = user.mention + " Du bist beim nächsten Spiel dabei!"
    reacmess = yield from send_message(channel, content)
    yield from add_reaction(reacmess, emoji)


@asyncio.coroutine
def new_poll(message):
    global gl_users
    global gl_roles
    arguments = message.content.split()
    length = len(arguments[0]) + len(arguments[1]) + 1
    content = "." + message.content[length:]
    if arguments[1].startswith('all'):
        for user in gl_users:
            bol_death = "Tot" in gl_users[user][0]['role']
            if not bol_death:
                emoji = gl_users[user][0]["emoji"]
                mention = gl_users[user][0]["mention"]
                content = content + "\n" + emoji + " " + mention
        yield from client.delete_message(message)
        recmess = yield from send_message(message.channel, content)
        for user in gl_users:
            emoji = gl_users[user][0]["emoji"]
            yield from add_reaction(recmess, emoji)
    else:
        for user in gl_users:
            bol_death = "Tot" in gl_users[user][0]['role']
            bol_role = user in gl_roles[arguments[1]][0]['user']
            if not bol_death and not bol_role:
                emoji = gl_users[user][0]["emoji"]
                mention = gl_users[user][0]["mention"]
                content = content + "\n" + emoji + " " + mention
        yield from client.delete_message(message)
        recmess = yield from send_message(message.channel, content)
        for user in gl_users:
            if not bol_death and not bol_role:
                emoji = gl_users[user][0]["emoji"]
                yield from add_reaction(recmess, emoji)


@asyncio.coroutine
def send_message(receiver, content):
    message = yield from client.send_message(receiver, content)
    return message


@asyncio.coroutine
def add_reaction(message, emoji):
    yield from client.add_reaction(message, emoji)


def dump_array(file, array):
    with open(file, "w") as file:
        file.write(json.dumps(array))


with open("BotToken.txt", "r") as file:
    token = file.read()
client.run(token)
