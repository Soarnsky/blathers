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
    "black": discord.Color(0),
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

    acnh_info = ""
    passport = get_passport(user)

    embed = discord.Embed(
        color=discord.Color.purple(),
        title="{}'s Passport".format(user.display_name)
    )

    if passport:
        if passport['ign']:
            acnh_info = f"{acnh_info}**ign:** {passport['ign']}\n"
        if passport['island']:
            acnh_info = f"{acnh_info}**island:** {passport['island']}\n"

        if passport['color']:
            embed.color = COLOR[passport['color']]  # change to new color if selected

        if passport['fruit'] or passport['friendcode'] or passport['nookexchange']:
            #if passport['nookexchange']:
            footer = f"{passport['friendcode']}\n + {passport['nookexchange']}"
            embed.set_footer(text=footer, icon_url=FRUIT[passport['fruit']])

        #if passport['nookexchange']:
            #embed.url = [Nookexchange](https://nookexchange/u/ibeenjammin)

    embed.set_thumbnail(url=user.avatar_url_as(format="png"))
    if acnh_info:
        embed.add_field(name="__**ACNH INFO**__", value=acnh_info)
    embed.add_field(name="__**SQUAD INFO**__",
                    value=f"**name:** {user.display_name}\n**joined:** {user.joined_at.__format__('%d %b %y')}")

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


def set_ign(user, name):
    with sqlite3.connect('passports.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE PASSPORT SET ign = ? WHERE user = ?", (name, user.id))
        conn.commit()


def set_island(user, name):
    with sqlite3.connect('passports.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE PASSPORT SET island = ? WHERE user = ?", (name, user.id))
        conn.commit()


def normalize_fruit(fruit):
    fruit = fruit.lower()
    for f in FRUIT:
        if f in fruit:
            return f
    return ""


def set_fruit(user, fruit):
    norm_fruit = normalize_fruit(fruit)
    if not norm_fruit:
        return ""
    else:
        with sqlite3.connect('passports.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE PASSPORT SET fruit = ? WHERE user = ?", (norm_fruit, user.id))
            conn.commit()
        return norm_fruit


def normalize_fc(fc):
    return re.sub(r'\D', "", fc)


def set_friend_code(user, fc):
    norm_fc = normalize_fc(fc)
    if len(norm_fc) != 12:
        return ""
    else:
        hyphened_fc = f"SW-{norm_fc[0:4]}-{norm_fc[4:8]}-{norm_fc[8:12]}"
        with sqlite3.connect('passports.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE PASSPORT SET friendcode = ? WHERE user = ?", (hyphened_fc, user.id))
            conn.commit()
        return hyphened_fc


def normalize_color(color):
    color = color.lower()
    for c in COLOR:
        if c in color:
            return c
    return ""


def set_color(user, color):
    norm_color = normalize_color(color)
    if not norm_color:
        return ""
    else:
        with sqlite3.connect('passports.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE PASSPORT SET color = ? WHERE user = ?", (norm_color, user.id))
            conn.commit()
        return norm_color


def set_nex(user, username):
    with sqlite3.connect('passports.db') as conn:
        url = f"[nook.exchange](https://nook.exchange/u/{username})"
        c = conn.cursor()
        c.execute("UPDATE PASSPORT SET nookexchange = ? WHERE user = ?", (url, user.id))
        conn.commit()

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
                  nookexchange TEXT,
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
        await ctx.send(f"{user.mention}, your ign has been set to {name}")

    @passport.command(pass_context=True)
    async def island(self, ctx, *, name):
        """Set your island name"""
        user = ctx.message.author
        set_island(user, name)
        await ctx.send(f"{user.mention}, your residency has been set to {name}")

    @passport.command(pass_context=True)
    async def fruit(self, ctx, fruit):
        """Set your native fruit"""
        user = ctx.message.author
        formatted_fruit = set_fruit(user, fruit)
        if formatted_fruit:
            await ctx.send(f"{user.mention}, your native fruit has been set to {formatted_fruit}")
        else:
            await ctx.send(f"Sorry {user.mention}, {fruit} is not a valid fruit.")

    @passport.command(pass_context=True)
    async def fc(self, ctx, fc):
        """Set your friend code"""
        user = ctx.message.author
        hyphened_fc = set_friend_code(user, fc)
        if hyphened_fc:
            await ctx.send(f"{user.mention}, your friend code has been set to {hyphened_fc}")
        else:
            await ctx.send(f"Ah, {user.mention}. it seems '{fc}' is not a valid code.")

    @passport.command(pass_context=True)
    async def color(self, ctx, color):
        """Set your passport color [blue, gold, green, magenta, orange, purple, red, teal]"""
        user = ctx.message.author
        formatted_color = set_color(user, color)
        if formatted_color:
            await ctx.send(f"{user.mention}, your passport is now {formatted_color}")
        else:
            await ctx.send(f"Ah, {user.mention}. it seems '{color}' is not a valid color.")

    @passport.command(pass_context=True)
    async def nex(self, ctx, username):
        """Set your nook.exchange user"""
        user = ctx.message.author
        set_nex(user, username)
        await ctx.send(f"{user.mention}, your nook.exchange username has been set to {username}")


def setup(client):
    client.add_cog(Passport(client, client.config))
