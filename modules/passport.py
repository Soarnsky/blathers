# passport.py
import discord
from discord.ext import commands
import sqlite3
import re

FRUIT = {
    "apple": "https://nookipedia.com/w/images/a/a0/Fruit_Apple_NH_Icon.png",
    "cherry": "https://nookipedia.com/w/images/e/e4/Fruit_Cherry_NH_Icon.png",
    "orange": "https://nookipedia.com/w/images/d/dc/Fruit_Orange_NH_Icon.png",
    "peach": "https://nookipedia.com/w/images/d/d4/Fruit_Peach_NH_Icon.png",
    "pear": "https://nookipedia.com/w/images/2/2d/Fruit_Pear_NH_Icon.png"
}

COLOR = {
    "blue": discord.Color.blue(),
    "gold": discord.Color.gold(),
    "green": discord.Color.green(),
    "magenta": discord.Color.magenta(),
    "orange": discord.Color.orange(),
    "purple": discord.Color.purple(),
    "red": discord.Color.red(),
    "teal": discord.Color.teal()
}

def create_passport_card(user):
    """
  Get information about you, or a specified user.

  `user`: The user who you want information about. Can be an ID, mention or name.
  """

    passport = get_passport(user)
    acnh_info = ""
    if passport['ign']:
        acnh_info = "{}**ign:** {}\n".format(acnh_info, passport['ign'])
    if passport['island']:
        acnh_info = "{}**island:** {}\n".format(acnh_info, passport['island'])

    passport_color = discord.Color.purple()   #default color
    if passport['color']:
        passport_color = passport['color']    #change to new color if selected

    embed = discord.Embed(
        color=passport_color,
        title="{}'s Passport".format(user.display_name)
    )
    embed.set_thumbnail(url=user.avatar_url_as(format="png"))
    embed.add_field(name="__**ACNH INFO**__", value=acnh_info)
    embed.add_field(name="__**SQUAD INFO**__",
                    value="""**nickname:** {}
                        **joined:** {}"""
                    .format(user.nick, user.joined_at.__format__('%d %b %y')))
    if passport['fruit'] or passport['friendcode']:
        embed.set_footer(text="{}".format(passport['friendcode']), icon_url=FRUIT[passport['fruit']])
    return embed


def get_passport(user):
    with sqlite3.connect('passports.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM PASSPORT WHERE user = ?", (user.id,))
        passport = c.fetchone()
        return passport


def initialize_user_passport(user):
    with sqlite3.connect('passports.db') as conn:
        c = conn.cursor()
        c.execute("DELETE FROM PASSPORT WHERE user = ?", (user.id,))
        c.execute("INSERT INTO PASSPORT (user) VALUES (?)", (user.id,))
        conn.commit()


# added
def set_ign(user, name):
    with sqlite3.connect('passports.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE PASSPORT SET ign = ? WHERE user = ?", (name, user.id))
        conn.commit()


# added
def set_island(user, name):
    with sqlite3.connect('passports.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE PASSPORT SET island = ? WHERE user = ?", (name, user.id))
        conn.commit()


# added
def normalize_fruit(fruit):
    fruit = fruit.lower()
    for f in FRUIT:
        if f in fruit:
            return f
    return ""


# added
def set_fruit(user, fruit):
    norm_fruit = normalize_fruit(fruit)
    if not norm_fruit:
        return False
    else:
        with sqlite3.connect('passports.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE PASSPORT SET fruit = ? WHERE user = ?", (norm_fruit, user.id))
            conn.commit()
        return True


# added
def normalize_fc(fc):
    return re.sub(r'\D', "", fc)


# added
def set_friend_code(user, fc):
    norm_fc = normalize_fc(fc)
    if len(norm_fc) != 12:
        return ""
    else:
        hyphened_fc = "SW-{}-{}-{}".format(norm_fc[0:4], norm_fc[4:8], norm_fc[8:12])
        with sqlite3.connect('passports.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE PASSPORT SET friendcode = ? WHERE user = ?", (hyphened_fc, user.id))
            conn.commit()
        return hyphened_fc


def initialize_passport():
    with sqlite3.connect('passports.db') as conn:
        c = conn.cursor()
        c.execute("SELECT NAME FROM sqlite_master WHERE type = \"table\" AND name = \"PASSPORT\"")
        if not c.fetchall():
            c.execute("""CREATE TABLE IF NOT EXISTS PASSPORT
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  ign TEXT,
                  island TEXT,
                  fruit TEXT,
                  friendcode TEXT,
                  color TEXT,
                  user TEXT NOT NULL)""")
            conn.commit()


class Passport(commands.Cog):
    """
  Player passports collection
  """

    def __init__(self, client, config):
        self.client = client
        self.config = config
        initialize_passport()

    @commands.group(pass_context=True, aliases=['pp'])
    async def passport(self, ctx):
        """Passport command containing friendcode and other info"""
        user = ctx.message.author
        with sqlite3.connect('passports.db') as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM PASSPORT WHERE user = ?", (user.id,))
            if not c.fetchall():
                initialize_user_passport(user)

            if ctx.invoked_subcommand is None:
                passport = create_passport_card(user)
                await ctx.send(embed=passport)

    @passport.command(pass_context=True)
    async def get(self, ctx, user: discord.Member = None):
        """Get a user passport card. Passing no arguments returns requesters card"""
        if not user:
            user = ctx.message.author

        passport = create_passport_card(user)
        await ctx.send(embed=passport)

    # New Commands start here
    @passport.command(pass_context=True)
    async def ign(self, ctx, *, name):
        """Set your ign"""
        user = ctx.message.author
        set_ign(user, name)
        await ctx.send("{}, your ign has been set to {}".format(user.mention, name))

    @passport.command(pass_context=True)
    async def island(self, ctx, *, name):
        """Set your island name"""
        user = ctx.message.author
        set_island(user, name)
        await ctx.send("{}, your residency has been set to {}".format(user.mention, name))

    @passport.command(pass_context=True)
    async def fruit(self, ctx, fruit):
        """Set your native fruit"""
        user = ctx.message.author
        if set_fruit(user, fruit):
            await ctx.send("{}, your native fruit has been set to {}".format(user.mention, fruit))
        else:
            await ctx.send("Sorry {}, {} is not a valid fruit.".format(user.mention, fruit))

    @passport.command(pass_context=True)
    async def fc(self, ctx, fc):
        """Set your friend code"""
        user = ctx.message.author
        hyphened_fc = set_friend_code(user, fc)
        if hyphened_fc:
            await ctx.send("{}, your friend code has been set to {}".format(user.mention, hyphened_fc))
        else:
            await ctx.send("Ah, {}. it seems '{}' is not a valid code.".format(user.mention, fc))


def setup(client):
    client.add_cog(Passport(client, client.config))
