import discord
import asyncio
import json
import random
import emoji

client = discord.Client()
gl_roles = ""
gl_users = ""


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
    ms = message
    global gl_roles
    global gl_users
    if message.server is not None:
        if message.author.server_permissions.administrator:
            if message.content.startswith('!start'):
                yield from start(message)
                return
            if message.content.startswith('!roles'):
                yield from roles(message, True)
                return
            if message.content.startswith('!addrole'):
                yield from add_role(message)
                return
            if message.content.startswith('!poll'):
                yield from new_poll(message)
                return
            if message.content.startswith('!tot'):
                yield from add_death(message)
                return
            if message.content.startswith('!cleanstart'):
                yield from clean_start(message)
                return
            if message.content.startswith('!cleanroles'):
                yield from clean_roles(message)
                return
            if message.content.startswith('!delrole'):
                yield from del_role(message)
                return
            if message.content.startswith('!autr'):
                yield from add_user_to_role(message)
                return
            if is_command('!deluser', ms):
                yield from del_user(message)
                return
            if message.content.startswith('!cleanuser'):
                yield from clean_user(message)
                return
            if message.content.startswith("!newgame"):
                yield from new_game(message)
        if message.content.startswith('!ping'):
            yield from add_reaction(message, '🏓')
            return
        if message.content.startswith('!roles'):
            yield from roles(message, False)
            return
        if message.content.startswith('!help'):
            yield from show_help(message)
            return
        if message.content.startswith('!players'):
            yield from players(message)
            return
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
                return


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


def is_command(command, message):
    if message.content.startswith(command):
        return True
    else:
        return False


def char_is_emoji(character):
    return character in emoji.UNICODE_EMOJI


@asyncio.coroutine
def start(message):
    global gl_roles
    global gl_users
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
    for user in gl_users:
        content = "In der nächsten Runde \"Werwolf\" hast du die Rolle **" + gl_users[user][0]["role"][
            0] + "**. Viel Spaß!"
        print("user: " + user)
        destination = discord.utils.get(message.server.members, id=user)
        print("des: " + str(destination))
        yield from send_message(destination, content)


@asyncio.coroutine
def show_help(message):
    with open("help.txt", "r") as file:
        text = file.read()
        yield from send_message(message.channel, text)


@asyncio.coroutine
def new_game(message):
    global gl_users
    global gl_roles
    gl_roles = {}
    gl_users = {}
    dump_array("roles.json", gl_roles)
    dump_array("user.json", gl_users)
    yield from send_message(message.channel,
                            "Ein neues Spiel wurde gestartet. Ihr könnt euch jetzt mit !reg und einem Emoji eurer Wahl regestrieren! @here")


@asyncio.coroutine
def clean_start(message):
    global gl_roles
    global gl_users
    for role in gl_roles:
        gl_roles[role][0]["user"] = []
    for user in gl_users:
        gl_users[user][0]["role"] = []
    dump_array("user.json", gl_users)
    dump_array("roles.json", gl_roles)
    yield from send_message(message.channel, "Start wurde aufgeräumt")


@asyncio.coroutine
def clean_roles(message):
    global gl_roles
    gl_roles = {}
    dump_array("roles.json", gl_roles)
    yield from send_message(message.channel, "Rollen wurden gelöscht.")


@asyncio.coroutine
def clean_user(message):
    global gl_users
    gl_users = {}
    dump_array("user.json", gl_users)
    yield from send_message(message.channel, "Spieler wurden gelöscht.")


@asyncio.coroutine
def del_role(message):
    global gl_roles
    global gl_users
    arguments = message.content.split()
    if arguments[1] in gl_roles:
        del gl_roles[arguments[1]]
        dump_array('roles.json', gl_roles)
        yield from send_message(message.channel, "Rolle " + arguments[1] + " wurde gelöscht.")
    else:
        yield from send_message(message.channel, "Die Rolle " + arguments[1] + " ist nicht vorhanden.")


@asyncio.coroutine
def del_user(ms):
    global gl_roles
    global gl_users
    arguments = ms.content.split()
    if arguments[1] in gl_users:
        del gl_users[arguments[1]]
        for role in gl_roles:
            del gl_roles[role][0]["user"][arguments[1]]
        dump_array('roles.json', gl_roles)
        dump_array('user.json', gl_users)
        yield from send_message(ms.channel, "Der User " + arguments[1] + " wurde gelöscht.")
    else:
        yield from send_message(ms.channel, "Der User " + arguments[1] + " ist nicht vorhanden.")


@asyncio.coroutine
def force_signup(ms):
    arguments = ms.content.split()
    user_obj = destination = discord.utils.get(ms.server.members, id=arguments[1])
    yield from register(user_obj, ms.channel, arguments[2])


@asyncio.coroutine
def players(message):
    global gl_roles
    global gl_users
    content = "**Es sind folgende Benutzer im Spiel:** (" + str(len(gl_users)) + ")\n"
    for user in gl_users:
        content += gl_users[user][0]["mention"] + gl_users[user][0]["emoji"] + "\n"
    yield from send_message(message.channel, content)


@asyncio.coroutine
def add_death(message):
    global gl_roles
    global gl_users
    arguments = message.content.split()
    gl_users[arguments[1]][0]["role"].append("Tot")
    dump_array("user.json", gl_users)
    yield from send_message(message.channel, gl_users[arguments[1]][0]["name"] + " ist nun tot.")


@asyncio.coroutine
def roles(message, admin):
    global gl_roles
    global gl_users
    number_of_roles = 0
    arguments = message.content.split()
    bol = False
    if len(arguments) > 1:
        if admin and arguments[1] == '-u':
            bol = True
    content_title = "**Rollen im Spiel:** ("
    content = ""
    for role in gl_roles:
        number_of_roles += gl_roles[role][0]['argument']
        content += "*" + str(gl_roles[role][0]["argument"]) + "x " + role + "* "
        if bol:

            content += ": "
            for user in gl_roles[role][0]['user']:
                content += gl_users[user][0]['name'] + " "
        content += "\n"
    content = content_title + str(number_of_roles) + ") \n\n" + content
    yield from send_message(message.channel, content)


@asyncio.coroutine
def add_role(message):
    global gl_roles
    global gl_users
    arguments = message.content.split()
    gl_roles[arguments[1]] = [{"user": [], "argument": int(arguments[2])}]
    dump_array("roles.json", gl_roles)
    yield from send_message(message.channel, "Die Rolle \"" + arguments[1] + "\" wurde hinzugefügt")


@asyncio.coroutine
def add_user_to_role(message):
    global gl_roles
    global gl_users
    arguments = message.content.split()
    user = arguments[1]
    role = arguments[2]
    if user in gl_users and role in gl_roles:
        gl_users[user][0]["role"].append(role)
        gl_roles[role][0]["user"].append(user)
        yield from send_message(message.channel, "User wurde erfolgreich zu " + role + " hinzugefügt.")
    else:
        yield from send_message(message.channel, "Ein Fehler ist aufgetreten.")


@asyncio.coroutine
def register(user, channel, emoji):
    global gl_roles
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
    global gl_roles
    global gl_users
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
            bol_death = "Tot" in gl_users[user][0]['role']
            if not bol_death:
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
            bol_death = "Tot" in gl_users[user][0]['role']
            bol_role = user in gl_roles[arguments[1]][0]['user']
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
