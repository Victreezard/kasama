import discord
import os
import random
from discord import Color
from discord.ext import commands
from dotenv import load_dotenv
from random_facts import get_random_fact
from randomizer import randomize
from valheim_api import search_pages as valsearch, get_page as valget


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')
wiki_url = 'https://valheim.fandom.com/'


def _create_wiki_url(title):
    if ' ' in title:
        title = title.replace(' ', '_')
    return wiki_url + title


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(f'{bot.user} is connected to the guild {guild.name} (id: {guild.id})')


@bot.command(name='valsearch', help=f'Search and return a list of pages from the {wiki_url} wiki')
async def search_val(ctx, *query):
    query = ' '.join(query)
    results = valsearch(query)
    if type(results) is list:
        # Join results hyperlinks with newlines
        results = '\n'.join(
            [f"[**{result}**]({_create_wiki_url(result)})" for result in results])
        embed = discord.Embed(
            title=f'Results for *{query}*', description=results, color=Color.blurple())
    else:
        embed = discord.Embed(title=results, color=Color.red())
    embed.set_footer(text=f'Requested by {ctx.author.display_name}')
    await ctx.send(embed=embed)


@bot.command(name='valget', help=f"Display a page's contents from the {wiki_url} wiki")
async def get_val(ctx, *query):
    page = valget(' '.join(query))
    if type(page) is dict:
        embed = discord.Embed(title=page.get('title'),
                              url=_create_wiki_url(page.get('title')),
                              description=page.get('description'), color=Color.purple())
        if page.get('fields'):
            for name, value in page.get('fields').items():
                embed.add_field(name=name, value=value)

        if page.get('thumbnail'):
            embed.set_thumbnail(url=page.get('thumbnail'))
    else:
        embed = discord.Embed(title=f'{page}', color=Color.red())

    embed.set_footer(text=f'Requested by {ctx.author.display_name}')
    await ctx.send(embed=embed)


@bot.command(name='factme', help='Responds with a random fact and its source')
async def get_fact(ctx):
    fact_title = 'Fact You'
    fact_text, fact_url = get_random_fact()
    embed = discord.Embed(title=fact_title, url=fact_url,
                          description=fact_text, color=Color.random())
    await ctx.send(embed=embed)


@bot.command(name='randomize', help="""Accepts space-separated choices and picks at random
Format:
  1. "text1 text2 text3" - This will always return ONE random pick
  2. "2 text1 text2 text3" - The number of returned picks depends on the first number given""")
async def randomize_input(ctx, *inputs):
    embed = discord.Embed(title=randomize(inputs), color=Color.blurple())
    await ctx.send(embed=embed)


bot.run(TOKEN)
