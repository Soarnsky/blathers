import string
import Levenshtein

import discord
from discord.ext import commands
import sqlite3

MATCHING_THRESHOLD = 80

ART = ["academic painting",
       "amazing painting",
       "basic painting",
       "calm painting",
       "common painting",
       "detailed painting",
       "dynamic painting",
       "famous painting",
       "flowery painting",
       "glowing painting",
       "graceful painting",
       "jolly painting",
       "moody painting",
       "moving painting",
       "mysterious painting",
       "nice painting",
       "perfect painting",
       "proper painting",
       "quaint painting",
       "scary painting",
       "scenic painting",
       "serene painting",
       "sinking painting",
       "solemn painting",
       "twinkling painting",
       "warm painting",
       "wild painting left half",
       "wild painting right half",
       "wistful painting",
       "worthy painting",
       "ancient statue",
       "beautiful statue",
       "familiar statue",
       "gallant statue",
       "great statue",
       "informative statue",
       "motherly statue",
       "mystic statue",
       "robust statue",
       "rock-head statue",
       "tremendous statue",
       "valiant statue",
       "warrior statue"]

SORT_ALPHABETICAL = """ORDER BY
                            CASE 
                                WHEN (art like 'left %') THEN SUBSTR(art, 6)
                                WHEN (art like 'right %') THEN SUBSTR(art, 7)
                                ELSE art 
                            END"""


def levenshtein_distance(str1, str2):
    l = Levenshtein.distance(str1, str2)
    m = max(len(str1), len(str2))
    return (1 - l / m) * 100


def normalize_art(art):
    norm_art = art.lower().translate(str.maketrans('', '', string.punctuation))
    highest_score = 0
    best_match = ""
    if norm_art not in ART:
        for a in ART:
            score = levenshtein_distance(a, norm_art)
            if score > highest_score:
                highest_score = score
                best_match = a

    if highest_score > MATCHING_THRESHOLD:
        return best_match

    return norm_art


def is_art(art):
    art = normalize_art(art)
    with sqlite3.connect('art.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM COLLECTION WHERE art = ?", (art,))
        result = c.fetchone()
        if result:
            return True
        else:
            return False


def has_art(user, art):
    art = normalize_art(art)
    with sqlite3.connect('art.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM COLLECTION WHERE owned = 1 AND art = ? AND user = ?", (art, user.id))
        result = c.fetchone()
        if result:
            return True
        else:
            return False


def list_for_trade(user, art):
    art = normalize_art(art)
    with sqlite3.connect('art.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM FOR_TRADE WHERE art = ? AND user = ?", (art, user.id))
        result = c.fetchone()
        if not result:
            c.execute("INSERT INTO FOR_TRADE (art, quantity, user) VALUES (?,?,?)", (art, 1, user.id))
        else:
            c.execute("UPDATE FOR_TRADE SET quantity = quantity + 1 WHERE art = ? AND user = ?", (art, user.id))
        conn.commit()


def get_collection(user):
    with sqlite3.connect('art.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(f"SELECT art FROM COLLECTION WHERE owned = 1 AND user = ? {SORT_ALPHABETICAL}", (user.id,))
        owned = [row['art'] for row in c.fetchall()]
        c.execute(f"SELECT art FROM COLLECTION WHERE owned = 0 AND user = ? {SORT_ALPHABETICAL}", (user.id,))
        missing = [row['art'] for row in c.fetchall()]
        return {'owned': owned, 'missing': missing}


def add_to_collection(user, art):
    with sqlite3.connect('art.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE COLLECTION SET owned = 1 WHERE art = ? AND user = ?", (art, user.id))
        conn.commit()


def remove_from_collection(user, art):
    with sqlite3.connect('art.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE COLLECTION SET owned = 0 WHERE art = ? AND user = ?", (art, user.id))
        conn.commit()


def remove_from_for_trade(user, art):
    art = normalize_art(art)
    with sqlite3.connect('art.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT quantity FROM FOR_TRADE WHERE art = ? AND user = ?", (art, user.id))
        result = c.fetchone()
        if result:
            if result['quantity'] == 1:
                c.execute("DELETE FROM FOR_TRADE WHERE art = ? AND user = ?", (art, user.id))
                conn.commit()
            else:
                c.execute("UPDATE FOR_TRADE SET quantity = quantity - 1 WHERE art = ? AND user = ?",
                          (art, user.id))
                conn.commit()
            return True
        else:
            return False


def initialize_user_collection(user, owned):
    art_tuples = []
    for art in ART:
        art_tuples.append((art, owned, user.id))
    with sqlite3.connect('art.db') as conn:
        c = conn.cursor()
        c.execute("DELETE FROM COLLECTION WHERE user = ?", (user.id,))
        c.execute("DELETE FROM FOR_TRADE WHERE user = ?", (user.id,))
        c.executemany("INSERT INTO COLLECTION VALUES (?,?,?)", art_tuples)
        conn.commit()


def initialize_collection():
    with sqlite3.connect('art.db') as conn:
        c = conn.cursor()
        c.execute("SELECT NAME FROM sqlite_master WHERE type = \"table\" AND name = \"COLLECTION\"")
        if not c.fetchall():
            c.execute("""CREATE TABLE IF NOT EXISTS COLLECTION 
                    (art TEXT NOT NULL,
                    owned INT,
                    user TEXT NOT NULL)""")
            conn.commit()


def initialize_for_trade():
    with sqlite3.connect('art.db') as conn:
        c = conn.cursor()
        c.execute("SELECT NAME FROM sqlite_master WHERE type = \"table\" AND name = \"FOR_TRADE\"")
        if not c.fetchall():
            c.execute("""CREATE TABLE IF NOT EXISTS FOR_TRADE 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    art TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    user TEXT NOT NULL)""")
            conn.commit()


class Art(commands.Cog):
    """
    Player art collection
    """

    def __init__(self, client, config):
        self.client = client
        self.config = config
        initialize_collection()
        initialize_for_trade()

    @commands.group(pass_context=True, aliases=['a'])
    async def art(self, ctx):
        """Art collection command"""
        user = ctx.message.author
        with sqlite3.connect('art.db') as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM COLLECTION WHERE user = ?", (user.id,))
            if not c.fetchall():
                initialize_user_collection(user, 0)

            if ctx.invoked_subcommand is None:
                result = get_collection(user)
                if not result['owned']:
                    await ctx.send("Hooooo... WHO?! {}! It appears you have yet to donate any art pieces... "
                                   "(.art add <art>)".format(user.mention))
                else:
                    missing = " ".join([f"`{item}`" for item in result['missing']])
                    if len(result['owned']) == len(ART):
                        await ctx.send(f"{user.mention} Owned: ALL art ({len(result['owned'])})")
                    else:
                        await ctx.send(f"{user.mention} Owned: {len(result['owned'])} art. Missing: {missing}")

    @art.command(pass_context=True)
    async def add(self, ctx, *, art):
        """Add art to your collection, else to For Trade if extra"""
        user = ctx.message.author
        art_list = [name.strip() for name in art.split(',')]
        ft_list = []
        collection_list = []
        invalid_list = []
        for art in art_list:
            art = normalize_art(art)
            if is_art(art):
                if has_art(user, art):
                    list_for_trade(user, art)
                    ft_list.append(art)
                else:
                    add_to_collection(user, art)
                    collection_list.append(art)
            else:
                invalid_list.append(art)

        ft_art = " ".join([f"`{a}`" for a in ft_list])
        collection_art = " ".join([f"`{a}`" for a in collection_list])
        invalid_art = " ".join([f"`{a}`" for a in invalid_list])

        message = f"{user.mention}, the following have been **added**:\n"
        if collection_art:
            message = f"{message}  - Collection: {collection_art}\n"
        if ft_art:
            message = f"{message}  - For Trade: {ft_art}\n"
        if invalid_art:
            message = f"{message}  - Invalid: {invalid_art}\n"

        await ctx.send(message)

    @art.command(pass_context=True)
    async def complete(self, ctx):
        """Adds all art pieces to your collection"""
        user = ctx.message.author
        initialize_user_collection(user, 1)
        await ctx.send(f"Astounding, {user.mention}! You've donated every last genuine art piece in existence!")

    @art.command(pass_context=True)
    async def rm(self, ctx, *, art):
        """Remove art from For Trade, else from collection"""
        user = ctx.message.author
        art_list = [name.strip() for name in art.split(',')]
        ft_list = []
        collection_list = []
        invalid_list = []
        none_list = []
        for art in art_list:
            art = normalize_art(art)
            if is_art(art):
                if has_art(user, art):
                    if remove_from_for_trade(user, art):
                        ft_list.append(art)
                    else:
                        remove_from_collection(user, art)
                        collection_list.append(art)
                else:
                    none_list.append(art)
            else:
                invalid_list.append(art)

        ft_art = " ".join([f"`{a}`" for a in ft_list])
        collection_art = " ".join([f"`{a}`" for a in collection_list])
        invalid_art = " ".join([f"`{a}`" for a in invalid_list])
        none_list = " ".join([f"`{a}`" for a in none_list])

        message = f"{user.mention}, the following have been **removed**:\n"
        if collection_art:
            message = f"{message}  - Collection: {collection_art}\n"
        if ft_art:
            message = f"{message}  - For Trade: {ft_art}\n"
        if none_list:
            message = f"{message}  - Don't Have: {none_list}\n"
        if invalid_art:
            message = f"{message}  - Invalid: {invalid_art}\n"

        await ctx.send(message)

    @art.command(pass_context=True)
    async def reset(self, ctx):
        """Use this command to reset your collection."""
        user = ctx.message.author
        initialize_user_collection(user, 0)
        await ctx.send(f"Hooooo... WHO?! {user.mention}! Where did all the art pieces go???")

    @art.command(pass_context=True)
    async def lf(self, ctx):
        """List of residents who have an art piece you need"""
        user = ctx.message.author
        arts = {}
        result = get_collection(user)
        with sqlite3.connect('art.db') as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            for art in result['missing']:
                c.execute("SELECT user FROM FOR_TRADE WHERE art = ?", (art,))
                result = c.fetchall()
                if result:
                    users = ", ".join([f"<@{row['user']}>" for row in result])
                    arts[art] = users
        message = ""
        for ft, users in arts.items():
            message = f"{message}  - `{ft}`: {users}\n"
        if message:
            await ctx.send(f"{user.mention}, a little birdy has given word that these residents may have the art "
                           f"pieces you seek!\n{message}")
        else:
            await ctx.send(f"{user.mention}, none of the art pieces you need are available for trade.")

    @art.command(pass_context=True)
    async def ft(self, ctx):
        """List of your extra art pieces"""
        user = ctx.message.author
        with sqlite3.connect('art.db') as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(f"SELECT * FROM FOR_TRADE WHERE user = ? {SORT_ALPHABETICAL}", (user.id,))
            result = c.fetchall()
            if result:
                art = "".join([f"  - `{row['art']}` **x{row['quantity']}**\n" for row in result])
                await ctx.send(f"{user.mention}, these are you extra art pieces:\n{art}")
            else:
                await ctx.send(f"{user.mention}, you have no extra art pieces listed for trade")

    @art.command(pass_context=True)
    async def list(self, ctx):
        """List of all art pieces."""
        user = ctx.message.author
        arts = " ".join([f"`{art}`" for art in ART])
        await ctx.send(f"{user.mention}, here is the current list of art pieces.\n{arts}")


def setup(client):
    client.add_cog(Art(client, client.config))
