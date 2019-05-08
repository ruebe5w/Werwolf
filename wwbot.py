import asyncio
import json
import random
import sys
import time

from discord.ext import commands
import discord
import emoji

prefix = "!"
bot = commands.Bot(command_prefix=prefix)
gl_roles = ""
gl_users = ""
user_object_force = ""


@bot.event
async def on_ready():
    print("Everything's all ready to go~")  #
    print(time.strftime("%d.%m.%Y %H:%M"))
    user_load()
    roles_load()


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


@bot.command()
async def ping(ctx):
    '''
    This text will be shown in the help command
    '''

    # Get the latency of the bot
    latency = bot.latency  # Included in the Discord.py library
    # Send it to the user
    await ctx.send(latency)


@bot.command()
@commands.has_role("Spielleiter")
async def start(ctx):
    """Startet das Spiel, weist Rollen zu"""
    message = ctx.message
    global gl_roles
    global gl_users
    user_arr = []
    for user_id in gl_users:
        user_arr.append(user_id)
    random.shuffle(user_arr)
    i = 0
    for role in gl_roles:
        for i2 in range(0, gl_roles[role][0]["argument"]):
            gl_roles[role][0]["user"].append(str(user_arr[i]))
            gl_users[user_arr[i]][0]["role"].append(role)
            i = i + 1
    dump_array('user.json', gl_users)
    dump_array('roles.json', gl_roles)
    content = "Das Spiel wurde gestartet! Folgende Rollen sind im Spiel:\n"
    await send_message(message.channel, content)
    await ctx.send(collect_roles(False))
    for user_id in gl_users:
        content = "In der nächsten Runde \"Werwolf\" hast du die Rolle **" + gl_users[user_id][0]["role"][
            0] + "**. Viel Spaß!"
        member = ctx.guild.get_member(int(user_id))
        await send_message(member.dm_channel, content)


"""
@asyncio.coroutine
def show_help(message):
    with open("help.txt", "r") as file:
        text = file.read()
        await send_message(message.channel, text)
"""


@bot.command(aliases=["newgame", "new"])
@commands.has_role("Spielleiter")
async def new_game(ctx):
    """Erstellt ein neues Spiel und loescht das vorherige."""
    message = ctx.message
    global gl_users
    global gl_roles
    gl_roles = {}
    gl_users = {}
    dump_array("roles.json", gl_roles)
    dump_array("user.json", gl_users)
    await send_message(message.channel,
                       "Ein neues Spiel wurde gestartet. "
                       "Ihr könnt euch jetzt mit !reg und einem Emoji eurer Wahl regestrieren! @here")


@bot.command(aliases=["cleanstart"])
@commands.has_role("Spielleiter")
async def clean_start(ctx):
    """Loescht Rollenzuweisung, Rollen und Spieler bleiben bestehen"""
    message = ctx.message
    global gl_roles
    global gl_users
    for role in gl_roles:
        gl_roles[role][0]["user"] = []
    for user in gl_users:
        gl_users[user][0]["role"] = []
    dump_array("user.json", gl_users)
    dump_array("roles.json", gl_roles)
    await send_message(message.channel, "Start wurde aufgeräumt")


@bot.command()
@commands.has_role("Spielleiter")
async def clean_roles(ctx):
    """Loescht alle Rollen"""
    message = ctx.message
    global gl_roles
    gl_roles = {}
    dump_array("roles.json", gl_roles)
    await send_message(message.channel, "Rollen wurden gelöscht.")


@bot.command()
@commands.has_role("Spielleiter")
async def clean_users(ctx):
    """Loescht alle Spieler"""
    message = ctx.message
    global gl_users
    gl_users = {}
    dump_array("user.json", gl_users)
    await send_message(message.channel, "Spieler wurden gelöscht.")


@bot.command()
@commands.has_role("Spielleiter")
async def del_roles(ctx, rolle):
    """Loescht eine Rolle"""
    message = ctx.message
    global gl_roles
    global gl_users

    if rolle in gl_roles:
        del gl_roles[rolle]
        dump_array('roles.json', gl_roles)
        await send_message(message.channel, "Rolle " + rolle + " wurde gelöscht.")
    else:
        await send_message(message.channel, "Die Rolle " + rolle + " ist nicht vorhanden.")


@bot.command()
@commands.has_role("Spielleiter")
async def del_user(ctx, user_id):
    """Loescht einen Spieler"""
    ms = ctx.message
    global gl_roles
    global gl_users

    if user_id in gl_users:
        del gl_users[user_id]
        for role in gl_roles:
            del gl_roles[role][0]["user"][user_id]
        dump_array('roles.json', gl_roles)
        dump_array('user.json', gl_users)
        await send_message(ms.channel, "Der User " + user_id + " wurde gelöscht.")
    else:
        await send_message(ms.channel, "Der User " + user_id + " ist nicht vorhanden.")


@bot.command()
@commands.has_role("Spielleiter")
async def force_signup(ctx, user_id, emoji):
    """Gewaltsames Anmelden :D"""
    global user_object_force
    ms = ctx.message
    user_object_force = discord.utils.get(ms.server.members, id=user_id)
    await register(ctx, emoji)


@bot.command()
@commands.has_role("Spielleiter")
async def players(ctx):
    """Zeigt die Mitspieler im Spiel an."""
    message = ctx.message
    global gl_roles
    global gl_users
    content = "**Es sind folgende Benutzer im Spiel:** (" + str(len(gl_users)) + ")\n"
    for user in gl_users:
        content += gl_users[user][0]["mention"] + gl_users[user][0]["emoji"] + "\n"
    await send_message(message.channel, content)


@bot.command(aliases=["adddeath", "death"])
@commands.has_role("Spielleiter")
async def add_death(ctx, user_id):
    """Fuegt einem Spieler die Rolle "Tot" hinzu
    Spieler-ID: Rechtsklick auf Discord-User, ID"""
    message = ctx.message
    global gl_roles
    global gl_users
    gl_users[user_id][0]["role"].append("Tot")
    dump_array("user.json", gl_users)
    await send_message(message.channel, gl_users[user_id][0]["name"] + " ist nun tot.")


def is_gamemaster(member):
    for role in member.roles:
        if role.name == "Spielleiter" or role.name == "Gamemaster":
            return True
        else:
            return False


def collect_roles(bolGamemaster):
    number_of_roles = 0
    content_title = "**Rollen im Spiel:** ("
    content = ""
    for role in gl_roles:
        number_of_roles += gl_roles[role][0]['argument']
        content += "*" + str(gl_roles[role][0]["argument"]) + "x " + role + "* "
        if bolGamemaster:

            content += ": "
            for user in gl_roles[role][0]['user']:
                content += gl_users[user][0]['name'] + " "
        content += "\n"
    content = content_title + str(number_of_roles) + ") \n\n" + content
    return content


@bot.command(aliases=["roles", "showroles"])
async def show_roles(ctx, *args):
    """Zeigt die Rollen im Spiel an.
    Für Spielleiter: zum Anzeigen von Mitspielern zu den Rollen irgendeinen weiteren
    Buchstaben als Argument hinzufügen, z.B. \"!roles a\""""
    message = ctx.message
    global gl_roles
    global gl_users

    bol = False
    if is_gamemaster(ctx.author) and len(args) > 0:
        bol = True
    content = collect_roles(bol)
    await send_message(message.channel, content)


@bot.command(aliases=["addrole", "addr"])
@commands.has_role("Spielleiter")
async def add_role(ctx, rolle, count):
    """Fuegt eine Rolle zum Spiel hinzu.
    Rollenname (z.B. Werwolf)
    Anzahl - Anzahl, wie oft die Rolle vergeben werden soll"""
    message = ctx.message
    global gl_roles
    global gl_users
    gl_roles[rolle] = [{"user": [], "argument": int(count)}]
    dump_array("roles.json", gl_roles)
    await send_message(message.channel, "Die Rolle \"" + rolle + "\" wurde hinzugefügt")


@bot.command(aliases=["autr"])
@commands.has_role("Spielleiter")
async def add_user_to_role(ctx, user, role):
    """Fügt Benutzer einer Rolle hinzu (Nötig bei Weißer Werwolf!)"""
    message = ctx.message
    global gl_roles
    global gl_users
    if user in gl_users and role in gl_roles:
        gl_users[user][0]["role"].append(role)
        gl_roles[role][0]["user"].append(user)
        await send_message(message.channel, "User wurde erfolgreich zu " + role + " hinzugefügt.")
    else:
        await send_message(message.channel, "Ein Fehler ist aufgetreten.")


@bot.command(aliases=["reg"])
async def register(ctx, emoji, *args):
    """Befehl zum Registrieren um mitzuspielen
    Emoji: Emoji deiner Wahl, mit dem du in Abstimmungen erscheinen möchtest."""
    global user_object_force
    if user_object_force != "":
        user = user_object_force
        user_object_force = ""
    else:
        user = ctx.author
    channel = ctx.channel
    global gl_roles
    global gl_users
    if not char_is_emoji(emoji):
        await send_message(channel,
                           user.mention + " Deine Nachricht enthält kein gültiges Emoji!")
        return
    for cur_user in gl_users:  # Userdatenbank durchsuchen
        # print(user)
        if user.id == cur_user:
            content = user.mention + " Du bist schon dabei!"
            await send_message(channel, content)
            return

    gl_users[user.id] = [{"name": user.name, "discriminator": user.discriminator,
                          "emoji": emoji, "mention": user.mention, "role": []}]

    dump_array("user.json", gl_users)
    content = user.mention + " Du bist beim nächsten Spiel dabei!"
    reacmess = await send_message(channel, content)
    await add_reaction(reacmess, emoji)


@bot.command(aliases=["poll", "newpoll"])
@commands.has_role("Spielleiter")
async def new_poll(ctx, rolle, *, text: str):
    """Erstellt eine Abstimmung.
    Eine Mention an alle wird automatisch angehängt.
    Rolle - all oder Rollenname(z.B. Werwolf)
Abstimmungstext - Text, der ueber der Abstimmung angezeigt werden soll"""
    message = ctx.message
    global gl_roles
    global gl_users

    text = text + " @everyone"
    if rolle == "all" or rolle == "alle":
        for user in gl_users:
            bol_death = "Tot" in gl_users[user][0]['role']
            if not bol_death:
                emoji = gl_users[user][0]["emoji"]
                mention = gl_users[user][0]["mention"]
                text = text + "\n" + emoji + " " + mention
        await message.delete()
        recmess = await send_message(ctx.channel, text)
        for user in gl_users:
            bol_death = "Tot" in gl_users[user][0]['role']
            if not bol_death:
                emoji = gl_users[user][0]["emoji"]
                await add_reaction(recmess, emoji)
    else:
        for user in gl_users:
            bol_death = "Tot" in gl_users[user][0]['role']
            bol_role = user in gl_roles[rolle][0]['user']
            if not bol_death and not bol_role:
                emoji = gl_users[user][0]["emoji"]
                mention = gl_users[user][0]["mention"]
                text = text + "\n" + emoji + " " + mention
        await message.delete()
        recmess = await send_message(message.channel, text)
        for user in gl_users:
            bol_death = "Tot" in gl_users[user][0]['role']
            bol_role = user in gl_roles[rolle][0]['user']
            if not bol_death and not bol_role:
                emoji = gl_users[user][0]["emoji"]
                await add_reaction(recmess, emoji)


async def send_message(receiver, content):
    message = await receiver.send(content)
    return message


@asyncio.coroutine
async def add_reaction(message, emoji):
    await message.add_reaction(emoji)


def dump_array(file, array):
    with open(file, "w") as file:
        file.write(json.dumps(array))


log = open("Werwolf.log", "a")
sys.stdout = log

with open("BotToken.txt", "r") as file:
    token = file.read()
bot.run(token)
