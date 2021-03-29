import discord
import os
import random
from discord import Color
from discord.ext import commands
from dotenv import load_dotenv
from random_facts import get_random_fact
from randomizer import randomize


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(f'{bot.user} is connected to the guild {guild.name} (id: {guild.id})')


@bot.command(name='factme', help='Responds with a random fact and its source')
async def get_fact(ctx):
    fact_title = 'Fact You'
    fact_text, fact_url = get_random_fact()
    embed = discord.Embed(title=fact_title, url=fact_url,
                          description=fact_text, color=Color.green())
    await ctx.send(embed=embed)


@bot.command(name='randomize', help="""Accepts space-separated choices and picks at random
Format:
  1. "text1 text2 text3" - This will always return ONE random pick
  2. "2 text1 text2 text3" - The number of returned picks depends on the first number given""")
async def randomize_input(ctx, *inputs):
    embed = discord.Embed(title=randomize(inputs), color=Color.blurple())
    await ctx.send(embed=embed)


bot.run(TOKEN)
