import discord
import os
import random
from discord import Color
from discord.ext import commands
from dotenv import load_dotenv
from random_facts import get_random_fact
from randomizer import randomize
from valheim_api import search_page as valsearch, get_page_details as valget


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')
val_wiki = 'https://valheim.fandom.com'


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(f'{bot.user} is connected to the guild {guild.name} (id: {guild.id})')


@bot.command(name='valsearch', help=f'Search from the {val_wiki} wiki')
async def search_val(ctx, *query):
    query = ' '.join(query)
    results = valsearch(query)
    if type(results) is list:
        # Join results hyperlinks with newlines
        results = '\n'.join(
            [f"[**{result}**]({val_wiki}/{result.replace(' ', '_')})" for result in results])
        embed = discord.Embed(
            title=f'Results for *{query}*', description=results, color=Color.blurple())
    else:
        embed = discord.Embed(title=results, color=Color.red())
    embed.set_footer(text=f'Requested by {ctx.author.display_name}')
    await ctx.send(embed=embed)


@bot.command(name='valget', help=f'Display info about an item from the {val_wiki} wiki')
async def get_val(ctx, *query):
    results = valget(' '.join(query))
    if type(results) is dict:
        embed = discord.Embed(title=results['title'], url=results['url'],
                              description=results['description'], color=Color.purple())
        if results.get('fields'):
            for name, value in results['fields'].items():
                if type(value) is list:
                    value = '\n'.join(value)

                embed.add_field(name=name, value=value)

        if results['thumbnail']:
            embed.set_thumbnail(url=results['thumbnail'])
    else:
        embed = discord.Embed(title=f'{results}', color=Color.red())

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
