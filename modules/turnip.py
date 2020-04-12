import string
import sqlite3

from discord.ext import commands
from modules import prediction

DAYS = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
TIME = ["am", "pm"]
PATTERNS = {
    0: "The Random",
    1: "High Spike",
    2: "Decreasing",
    3: "Small Spike"
}


def normalize_day(day):
    day = day.lower()
    for d in DAYS:
        if d in day:
            return d
    return ""


def normalize_time(time):
    time = time.lower().translate(str.maketrans('', '', string.punctuation))
    for t in TIME:
        if t in time:
            return t
    return ""


def get_turnips(user):
    with sqlite3.connect('turnips.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM TURNIPS WHERE user = ?", (user.id,))
        result = c.fetchone()
        return result


def get_patterns(user):
    turnips = get_turnips(user)
    sell_prices = []
    for key in turnips.keys():
        if key == "user":
            continue
        if key == "base_price":
            sell_prices = [turnips['base_price'], turnips['base_price']]
            continue
        sell_prices.append(turnips[key])

    return prediction.analyze_possibilities(sell_prices)


def pretty_print_turnips(user):
    result = get_turnips(user)
    message = ""
    for key in result.keys():
        if key == 'user':
            continue
        if result[key]:
            message = "{}  - `{}: {}`\n".format(message, key, result[key])

    return message


def set_turnip_price(user, day, time, price):
    day = normalize_day(day)
    time = normalize_time(time)
    if not day or not time:
        return False
    with sqlite3.connect('turnips.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE TURNIPS SET {}_{} = ? WHERE user = ?".format(day, time), (price, user.id))
        conn.commit()
        return True


def initialize_user_turnips(user):
    with sqlite3.connect('turnips.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO TURNIPS (user) VALUES (?)", (user.id,))
        conn.commit()


def initialize_turnips():
    with sqlite3.connect('turnips.db') as conn:
        c = conn.cursor()
        if not c.fetchall():
            c.execute("""CREATE TABLE IF NOT EXISTS TURNIPS
                        (base_price INTEGER,
                        mon_am INTEGER,
                        mon_pm INTEGER,
                        tue_am INTEGER,
                        tue_pm INTEGER,
                        wed_am INTEGER,
                        wed_pm INTEGER,
                        thu_am INTEGER,
                        thu_pm INTEGER,
                        fri_am INTEGER,
                        fri_pm INTEGER,
                        sat_am INTEGER,
                        sat_pm INTEGER,
                        user TEXT NOT NULL)""")
        conn.commit()


class Turnip(commands.Cog):
    """
    Player fossils collection
    """

    def __init__(self, client, config):
        self.client = client
        self.config = config
        initialize_turnips()

    @commands.group(pass_context=True, aliases=['t'])
    async def turnip(self, ctx):
        """Turnip price command"""
        user = ctx.message.author
        with sqlite3.connect('turnips.db') as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM TURNIPS WHERE user = ?", (user.id,))
            if not c.fetchone():
                initialize_user_turnips(user)

        if ctx.invoked_subcommand is None:
            message = pretty_print_turnips(user)
            patterns = get_patterns(user)
            if patterns:
                p = patterns[-1]
                if p["week_max"] < p["week_min"]:
                    message = "{}\nNo patterns match your data, please check the values.\n*Note: Predictions are " \
                              "unavailable for your first week.*".format(message)
                else:
                    message = "{}\n\n**Best Possible Price: {}**\n{}:```".format(message, p["week_max"], p["pattern_description"])
                    day = 0
                    time = 0
                    for half_day in p["prices"]:
                        weekday = DAYS[day]
                        daytime = TIME[time % 2]
                        if time % 2 == 1:
                            day += 1
                        time += 1
                        if half_day["min"] == half_day["max"]:
                            continue
                        message = "{}\n  {} {} - {}..{}".format(message, weekday, daytime, half_day["min"], half_day["max"])
                    message = "{}```".format(message)
            await ctx.send("{}, your stalk market data:\n{}".format(user.mention, message))

    @turnip.command(pass_context=True)
    async def bp(self, ctx, bp):
        """Add your Sunday Daisy Mae base price"""
        user = ctx.message.author
        with sqlite3.connect('turnips.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE TURNIPS SET base_price = ? WHERE user = ?", (bp, user.id))
            conn.commit()
            await ctx.send("{}, your Sunday Daisy Mae base price updated to D${}".format(user.mention, bp))

    @turnip.command(pass_context=True)
    async def set(self, ctx, day, time, price):
        """Set your nookling sell prices for each half day"""
        user = ctx.message.author
        if set_turnip_price(user, day, time, price):
            await ctx.send(
                "{}, your {}_{} price set to {}".format(user.mention, normalize_day(day), normalize_time(time), price))
        else:
            await ctx.send("{}, invalid date/time.".format(user.mention))


def setup(client):
    client.add_cog(Turnip(client, client.config))