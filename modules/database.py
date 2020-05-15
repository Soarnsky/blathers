import string
import requests
import json

import discord
from discord.ext import commands

SERVER = "http://acnhapi.com"
ENDPOINTS = {
    "fish": "fish",
    "bugs": "bugs",
    "fossils": "fossils",
    "villagers": "villagers",
    "icons": "icons",
    "images": "images"
}


def normalize_text(text):
    norm_text = text.lower().translate(str.maketrans('', '', string.punctuation))
    return norm_text


def get_id(type, name):
    if type == 'villagers':
        uri = f"{SERVER}/{ENDPOINTS['villagers']}"
        response = requests.get(uri)
        if response.ok:
            villager_data = json.loads(response.text)
            for villager, data in villager_data.items():
                if data['name']['name-en'].lower() == normalize_text(name):
                    return villager
    else:
        return "_".join(name.split())
    return ""


def convert_to_image(content, type, name):
    filename = f'{type}-{name}.png'
    with open(f'data/{filename}', "wb") as f:
        f.write(content)
    return filename


class Database(commands.Cog):
    """
    ACNH Database query command
    """

    def __init__(self, client, config):
        self.client = client
        self.config = config

    @commands.group(pass_context=True, aliases=['db'])
    async def database(self, ctx):
        """Database query command"""
        user = ctx.message.author

        if ctx.invoked_subcommand is None:
            endpoints = ", ".join([v for v in ENDPOINTS.values()])
            await ctx.send(
                f"Database query command, {user.mention}! Choose which category you'd like to query\n\t{endpoints}")

    @database.command(pass_context=True, aliases=['fi'])
    async def fish(self, ctx, *, f):
        """Adds all databases to your collection"""
        user = ctx.message.author
        fish = get_id('fish', f)
        uri = f"{SERVER}/{ENDPOINTS['fish']}/{fish}"
        response = requests.get(uri)
        if response.ok:
            await ctx.send(f"{user.mention}, ```{response.text}```")
        else:
            await ctx.send(f"Sorry, {user.mention}... Unable to find {f}.")

    @database.command(pass_context=True, aliases=['b'])
    async def bugs(self, ctx, *, b):
        """Adds all databases to your collection"""
        user = ctx.message.author
        bug = get_id('bugs', b)
        uri = f"{SERVER}/{ENDPOINTS['bugs']}/{bug}"
        response = requests.get(uri)
        if response.ok:
            await ctx.send(f"{user.mention}, ```{response.text}```")
        else:
            await ctx.send(f"Sorry, {user.mention}... Unable to find {b}.")

    @database.command(pass_context=True, aliases=['fo'])
    async def fossils(self, ctx, *, f):
        """Adds all databases to your collection"""
        user = ctx.message.author
        fossil = get_id('fossils', f)
        uri = f"{SERVER}/{ENDPOINTS['fossils']}/{fossil}"
        response = requests.get(uri)
        if response.ok:
            await ctx.send(f"{user.mention}, ```{response.text}```")
        else:
            await ctx.send(f"Sorry, {user.mention}... Unable to find {f}.")

    @database.command(pass_context=True, aliases=['v'])
    async def villagers(self, ctx, v):
        """Adds all databases to your collection"""
        user = ctx.message.author
        villager = get_villager_id(v)
        if villager:
            uri = f"{SERVER}/{ENDPOINTS['villagers']}/{villager}"
            response = requests.get(uri)
            if response.ok:
                await ctx.send(f"{user.mention}, ```{response.text}```")
        else:
            await ctx.send(f"Sorry, {user.mention}... Unable to find {v}.")

    @database.command(pass_context=True, aliases=['icon'])
    async def icons(self, ctx, type, *, i):
        """Adds all databases to your collection"""
        user = ctx.message.author
        if ENDPOINTS.get(type):
            item = get_id(type, i)
            uri = f"{SERVER}/{ENDPOINTS['icons']}/{ENDPOINTS[type]}/{item}"
            response = requests.get(uri)
            if response.ok:
                filename = convert_to_image(response.content, 'icon', item)
                icon = discord.File(f'data/{filename}', filename=filename)
                await ctx.send(f"{user.mention}", file=icon)
            else:
                await ctx.send(f"Sorry, {user.mention}... Unable to find {b}.")
        else:
            await ctx.send(f"Sorry, {user.mention}... {type} is not a valid category.")

    @database.command(pass_context=True, aliases=['img'])
    async def images(self, ctx, type, *, i):
        """Adds all databases to your collection"""
        user = ctx.message.author
        if ENDPOINTS.get(type):
            item = get_id(type, i)
            uri = f"{SERVER}/{ENDPOINTS['images']}/{ENDPOINTS[type]}/{item}"
            response = requests.get(uri)
            if response.ok:
                filename = convert_to_image(response.content, 'img', item)
                image = discord.File(f'data/{filename}', filename=filename)
                await ctx.send(f"{user.mention}", file=image)
            else:
                await ctx.send(f"Sorry, {user.mention}... Unable to find {b}.")
        else:
            await ctx.send(f"Sorry, {user.mention}... {type} is not a valid category.")


def setup(client):
    client.add_cog(Database(client, client.config))
