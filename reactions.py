import discord
import asyncio
import json

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

        if message.content.startswith('!roles'):
            yield from roles(message, True)
        if message.content.startswith('!addrole'):
            yield from add_role(message)
        if message.content.startswith('!p'):
            yield from new_poll(message)
    else:
        if message.content.startswith('!r'):
            contains_emoji = False
            for i in message.content:
                print(hex(ord(i)))
                if 0x1F600 <= int(hex(ord(i)), 16) <= 0x1F64F:
                    contains_emoji = True
                    yield from add_reaction(message, i)
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
            print(role)
            content += ": " + gl_roles[role][0]['user']
        content += "\n"
    yield from send_message(message.channel, content)


@asyncio.coroutine
def add_role(message):
    global gl_roles
    arguments = message.content.split()
    gl_roles[arguments[1]] = [{"user": [{}]}]
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
                          "emoji": emoji, "mention": user.mention}]

    dump_array("user.json", gl_users)
    content = user.mention + " Du bist beim nächsten Spiel dabei!"
    reacmess = yield from send_message(channel, content)
    yield from add_reaction(reacmess, emoji)


@asyncio.coroutine
def new_poll(message):
    global gl_users
    content = message.content[2:]
    for user in gl_users:
        emoji = gl_users[user][0]["emoji"]
        mention = gl_users[user][0]["mention"]
        content = content + "\n" + emoji + " " + mention
    yield from client.delete_message(message)
    recmess = yield from send_message(message.channel, content)
    for user in gl_users:
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
