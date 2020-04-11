import string

import discord
from discord.ext import commands
import sqlite3

FOSSILS = ["acanthostega",
           "amber",
           "ammonite",
           "ankylo skull",
           "ankylo tail",
           "ankylo torso",
           "anomalocaris",
           "archaeopteryx",
           "archelon skull",
           "archelon tail",
           "australopith",
           "brachio chest",
           "brachio pelvis",
           "brachio skull",
           "brachio tail",
           "coprolite",
           "deinony torso",
           "deinony tail",
           "dimetrodon skull",
           "dimetrodon torso",
           "dinosaur track",
           "diplo chest",
           "diplo neck",
           "diplo pelvis",
           "diplo skull",
           "diplo tail",
           "diplo tail tip",
           "dunkleosteus",
           "eusthenopteron",
           "iguanodon skull",
           "iguanodon tail",
           "iguanodon torso",
           "juramaia",
           "mammoth skull",
           "mammoth torso",
           "megacero skull",
           "megacero tail",
           "megacero torso",
           "left megalo side",
           "right megalo side",
           "myllokunmingia",
           "ophthalmo skull",
           "ophthalmo torso",
           "pachy skull",
           "pachy tail",
           "parasaur skull",
           "parasaur tail",
           "parasaur torso",
           "plesio skull",
           "plesio body",
           "plesio tail",
           "left ptera wing",
           "right ptera wing",
           "ptera body",
           "left quetzal wing",
           "right quetzal wing",
           "quetzal torso",
           "sabertooth skull",
           "sabertooth tail",
           "shark tooth pattern",
           "spino skull",
           "spino tail",
           "spino torso",
           "stego skull",
           "stego tail",
           "stego torso",
           "trex skull",
           "trex tail",
           "trex torso",
           "tricera skull",
           "tricera tail",
           "tricera torso",
           "trilobite"]


def normalize_fossil(fossil):
    return fossil.lower().translate(str.maketrans('', '', string.punctuation))


def is_fossil(fossil):
    fossil = normalize_fossil(fossil)
    with sqlite3.connect('fossils.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM COLLECTION WHERE fossil = ?", (fossil,))
        result = c.fetchone()
        if result:
            return True
        else:
            return False


def has_fossil(user, fossil):
    fossil = normalize_fossil(fossil)
    with sqlite3.connect('fossils.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM COLLECTION WHERE owned = 1 AND fossil = ? AND user = ?", (fossil, user.id))
        result = c.fetchone()
        if result:
            return True
        else:
            return False


def list_for_trade(user, fossil):
    fossil = normalize_fossil(fossil)
    with sqlite3.connect('fossils.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM FOR_TRADE WHERE fossil = ? AND user = ?", (fossil, user.id))
        result = c.fetchone()
        if not result:
            c.execute("INSERT INTO FOR_TRADE (fossil, quantity, user) VALUES (?,?,?)", (fossil, 1, user.id))
        else:
            c.execute("UPDATE FOR_TRADE SET quantity = quantity + 1 WHERE fossil = ? AND user = ?", (fossil, user.id))
        conn.commit()


def get_collection(user):
    with sqlite3.connect('fossils.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT fossil FROM COLLECTION WHERE owned = 1 AND user = ?", (user.id,))
        owned = [row['fossil'] for row in c.fetchall()]
        c.execute("SELECT fossil FROM COLLECTION WHERE owned = 0 AND user = ?", (user.id,))
        missing = [row['fossil'] for row in c.fetchall()]
        return {'owned': owned, 'missing': missing}


def add_to_collection(user, fossil):
    with sqlite3.connect('fossils.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE COLLECTION SET owned = 1 WHERE fossil = ? AND user = ?", (fossil, user.id))
        conn.commit()


def remove_from_collection(user, fossil):
    with sqlite3.connect('fossils.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE COLLECTION SET owned = 0 WHERE fossil = ? AND user = ?", (fossil, user.id))
        conn.commit()


def remove_from_for_trade(user, fossil):
    fossil = normalize_fossil(fossil)
    with sqlite3.connect('fossils.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT quantity FROM FOR_TRADE WHERE fossil = ? AND user = ?", (fossil, user.id))
        result = c.fetchone()
        if result:
            if result['quantity'] == 1:
                c.execute("DELETE FROM FOR_TRADE WHERE fossil = ? AND user = ?", (fossil, user.id))
                conn.commit()
            else:
                c.execute("UPDATE FOR_TRADE SET quantity = quantity - 1 WHERE fossil = ? AND user = ?",
                          (fossil, user.id))
                conn.commit()
            return True
        else:
            return False


def initialize_user_collection(user, owned):
    fossil_tuples = []
    for fossil in FOSSILS:
        fossil_tuples.append((fossil, owned, user.id))
    with sqlite3.connect('fossils.db') as conn:
        c = conn.cursor()
        c.execute("DELETE FROM COLLECTION WHERE user = ?", (user.id,))
        c.execute("DELETE FROM FOR_TRADE WHERE user = ?", (user.id,))
        c.executemany("INSERT INTO COLLECTION VALUES (?,?,?)", fossil_tuples)
        conn.commit()


def initialize_collection():
    with sqlite3.connect('fossils.db') as conn:
        c = conn.cursor()
        c.execute("SELECT NAME FROM sqlite_master WHERE type = \"table\" AND name = \"COLLECTION\"")
        if not c.fetchall():
            c.execute("""CREATE TABLE IF NOT EXISTS COLLECTION 
                    (fossil TEXT NOT NULL,
                    owned INT,
                    user TEXT NOT NULL)""")
            conn.commit()


def initialize_for_trade():
    with sqlite3.connect('fossils.db') as conn:
        c = conn.cursor()
        c.execute("SELECT NAME FROM sqlite_master WHERE type = \"table\" AND name = \"FOR_TRADE\"")
        if not c.fetchall():
            c.execute("""CREATE TABLE IF NOT EXISTS FOR_TRADE 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fossil TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    user TEXT NOT NULL)""")
            conn.commit()


class Fossil(commands.Cog):
    """
    Player fossils collection
    """

    def __init__(self, client, config):
        self.client = client
        self.config = config
        initialize_collection()
        initialize_for_trade()

    @commands.group(pass_context=True, aliases=['f'])
    async def fossil(self, ctx):
        """Fossil collection command"""
        user = ctx.message.author
        with sqlite3.connect('fossils.db') as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM COLLECTION WHERE user = ?", (user.id,))
            if not c.fetchall():
                initialize_user_collection(user, 0)

            if ctx.invoked_subcommand is None:
                result = get_collection(user)
                if not result['owned']:
                    await ctx.send("Hooooo... WHO?! {}! Looks like you haven't donated any fossils... "
                                   "(.fossil add <fossil>)".format(user.mention))
                else:
                    missing = " ".join(["`{}`".format(item) for item in result['missing']])
                    if len(result['owned']) == len(FOSSILS):
                        await ctx.send("{} Owned: ALL fossils ({})".format(user.mention, len(result['owned'])))
                    else:
                        await ctx.send(
                            "{} Owned: {} fossils. Missing: {}".format(user.mention, len(result['owned']), missing))

    @fossil.command(pass_context=True)
    async def add(self, ctx, *, fossils):
        """Add fossil to your collection, else to For Trade if extra"""
        user = ctx.message.author
        fossil_list = [name.strip() for name in fossils.split(',')]
        ft_list = []
        collection_list = []
        invalid_list = []
        for fossil in fossil_list:
            fossil = normalize_fossil(fossil)
            if is_fossil(fossil):
                if has_fossil(user, fossil):
                    list_for_trade(user, fossil)
                    ft_list.append(fossil)
                else:
                    add_to_collection(user, fossil)
                    collection_list.append(fossil)
            else:
                invalid_list.append(fossil)

        ft_fossils = " ".join(["`{}`".format(f) for f in ft_list])
        collection_fossils = " ".join(["`{}`".format(f) for f in collection_list])
        invalid_fossils = " ".join(["`{}`".format(f) for f in invalid_list])

        message = ""
        valid = ""
        if collection_fossils:
            valid = "{}  - Collection: {}\n".format(valid, collection_fossils)
        if ft_fossils:
            valid = "{}  - For Trade: {}\n".format(valid, ft_fossils)
        if valid:
            message = "{}, the following have been **added**:\n{}".format(user.mention, valid)

        invalid = ""
        if invalid_fossils:
            invalid = "{}  - Invalid: {}\n".format(invalid, invalid_fossils)
        if invalid:
            message = "{}, please double check these:\n{}".format(user.mention, invalid)
        await ctx.send(message)

    @fossil.command(pass_context=True)
    async def complete(self, ctx):
        """Adds all fossils to your collection"""
        user = ctx.message.author
        initialize_user_collection(user, 1)
        await ctx.send("Inconceivable, {}! You have donated every single fossil there is!".format(user.mention))

    @fossil.command(pass_context=True)
    async def rm(self, ctx, *, fossils):
        """Remove fossil from For Trade, else from collection"""
        user = ctx.message.author
        fossil_list = [name.strip() for name in fossils.split(',')]
        ft_list = []
        collection_list = []
        invalid_list = []
        none_list = []
        for fossil in fossil_list:
            fossil = normalize_fossil(fossil)
            if is_fossil(fossil):
                if has_fossil(user, fossil):
                    if remove_from_for_trade(user, fossil):
                        ft_list.append(fossil)
                    else:
                        remove_from_collection(user, fossil)
                        collection_list.append(fossil)
                else:
                    none_list.append(fossil)
            else:
                invalid_list.append(fossil)

        ft_fossils = " ".join(["`{}`".format(f) for f in ft_list])
        collection_fossils = " ".join(["`{}`".format(f) for f in collection_list])
        invalid_fossils = " ".join(["`{}`".format(f) for f in invalid_list])
        none_list = " ".join(["`{}`".format(f) for f in none_list])

        message = ""
        valid = ""
        if collection_fossils:
            valid = "{}  - Collection: {}\n".format(valid, collection_fossils)
        if ft_fossils:
            valid = "{}  - For Trade: {}\n".format(valid, ft_fossils)
        if valid:
            message = "{}, the following have been **removed**:\n{}".format(user.mention, valid)

        invalid = ""
        if invalid_fossils:
            invalid = "{}  - Invalid: {}\n".format(invalid, invalid_fossils)
        if none_list:
            invalid = "{}  - None: {}\n".format(invalid, none_list)
        if invalid:
            message = "{}, please double check these:\n{}".format(user.mention, invalid)
        await ctx.send(message)

    @fossil.command(pass_context=True)
    async def reset(self, ctx):
        """Use this command to reset your collection."""
        user = ctx.message.author
        initialize_user_collection(user, 0)
        await ctx.send("Hooooo... WHO?! {}! Where did all the fossils go???".format(user.mention))

    @fossil.command(pass_context=True)
    async def lf(self, ctx):
        """List of residents who have a fossil you need"""
        user = ctx.message.author
        fossils = {}
        result = get_collection(user)
        with sqlite3.connect('fossils.db') as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            for fossil in result['missing']:
                c.execute("SELECT user FROM FOR_TRADE WHERE fossil = ?", (fossil,))
                result = c.fetchall()
                if result:
                    users = ", ".join(["<@{}>".format(row['user']) for row in result])
                    fossils[fossil] = users
        message = ""
        for ft, users in fossils.items():
            message = "{}  - `{}`: {}\n".format(message, ft, users)
        if message:
            await ctx.send("{}, send these residents a hoot for fossils you need!\n\n{}".format(user.mention, message))
        else:
            await ctx.send("{}, none of the fossils you need are available for trade.".format(user.mention))

    @fossil.command(pass_context=True)
    async def ft(self, ctx):
        """List of your extra fossils"""
        user = ctx.message.author
        with sqlite3.connect('fossils.db') as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT quantity, fossil FROM FOR_TRADE WHERE user = ?", (user.id,))
            result = c.fetchall()
            if result:
                fossils = "".join(["  - `{}` **x{}**\n".format(row['fossil'], row['quantity']) for row in result])
                await ctx.send("{}, these are your extra fossils:\n\n {}".format(user.mention, fossils))
            else:
                await ctx.send("{}, you have no extra fossils listed for trade".format(user.mention))

    @fossil.command(pass_context=True)
    async def list(self, ctx):
        """List of all fossils."""
        user = ctx.message.author
        fossils = " ".join(["`{}`".format(fossil) for fossil in FOSSILS])
        await ctx.send("{}, here is the current list of fossils.\n{}".format(user.mention, fossils))


    @fossil.command(pass_context=True)
    async def cp(self, ctx):


    # @fossil.command(pass_context=True)
    # async def sync(self, ctx):
    #     with sqlite3.connect('fossils.db') as conn:
    #         conn.row_factory = sqlite3.Row
    #         c = conn.cursor()
    #         c.execute("""UPDATE COLLECTION
    #         SET fossil = ?
    #         WHERE fossil = ?""", ("deinony tail", "denoiny tail"))
    #         c.execute("""UPDATE FOR_TRADE
    #         SET fossil = ?
    #         WHERE fossil = ?""", ("deinony tail", "denoiny tail"))
    #         conn.commit()

    # @fossil.command(pass_context=True)
    # async def dedupe(self, ctx):
    #     with sqlite3.connect('fossils.db') as conn:
    #         conn.row_factory = sqlite3.Row
    #         c = conn.cursor()
    #         c.execute("DELETE FROM COLLECTION WHERE rowid NOT IN (SELECT min(rowid) FROM COLLECTION GROUP BY fossil, user)")
    #         conn.commit()

    # @fossil.command(pass_context=True)
    # async def copy(self, ctx):
    #     """TEMPORARY. Copying individual collections to collection table"""
    #     user = ctx.message.author
    #     collection = get_collection_table_name(user)
    #     fossil_tuples = []
    #     with sqlite3.connect('fossils.db') as conn:
    #         conn.row_factory = sqlite3.Row
    #         c = conn.cursor()
    #         c.execute("SELECT * FROM {}".format(collection))
    #         result = c.fetchall()
    #         if result:
    #             for row in result:
    #                 fossil_tuples.append((row['fossil'], row['owned'], user.id))
    #                 c.executemany("INSERT INTO COLLECTION VALUES (?,?,?)", fossil_tuples)
    #                 conn.commit()
    #             c.execute("DROP TABLE IF EXISTS {}".format(collection))
    #             conn.commit()
    #             await ctx.send("Copied over collection!")
    #         else:
    #             await ctx.send("No collection to copy over.")

    # @fossil.command(pass_context=True)
    # async def debug(self, ctx):
    #     user = ctx.message.author
    #     with sqlite3.connect('fossils.db') as conn:
    #         conn.row_factory = sqlite3.Row
    #         c = conn.cursor()
    #         c.execute("SELECT * FROM COLLECTION_{}".format(user.id))
    #         result = c.fetchall()
    #         if result:
    #             res1 = result[len(result) // 2:]
    #             res2 = result[:len(result) // 2]
    #             await ctx.send(["{}, {}".format(row['fossil'], row['owned']) for row in res1])
    #             await ctx.send(["{}, {}".format(row['fossil'], row['owned']) for row in res2])
    #         else:
    #             await ctx.send("Empty collections")
    #
    #         c.execute("SELECT * FROM FOR_TRADE".format(user.id))
    #         result = c.fetchall()
    #         if result:
    #             res1 = result[len(result) // 2:]
    #             res2 = result[:len(result) // 2]
    #             await ctx.send(["{}, <@{}>".format(row['fossil'], row['user']) for row in res1])
    #             await ctx.send(["{}, <@{}>".format(row['fossil'], row['user']) for row in res2])
    #         else:
    #             await ctx.send("Empty collections")


def setup(client):
    client.add_cog(Fossil(client, client.config))
