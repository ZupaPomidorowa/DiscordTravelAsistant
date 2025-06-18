import discord
from discord.ext import commands
from attractions import *
import os

discord_key = os.environ.get('DISCORD_KEY')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command(name='find_route', help='Find the route between two locations and finds attractions on way in Warsaw.\nUsage: !find_route <origin> <destination> <number_of_attractions> <travel_mode>')
async def find_route(ctx, origin, dest, num: int, mode):

    latlong_origin = check_address(origin)
    latlong_dest = check_address(dest)
    travel_mode = check_travel_mode(mode)

    await ctx.send('Got it! Finding a route with attractions')

    top_attractions, attraction_names = find_attractions(latlong_origin, latlong_dest, num, travel_mode)

    url = create_url(latlong_origin, latlong_dest, top_attractions, travel_mode)

    attraction_names_str =  '\n'.join([f'{i + 1}. {name}' for i, name in enumerate(attraction_names)])
    await ctx.send(f"Route with {num} best attractions: \n{attraction_names_str}")

    await ctx.send(f'Link to your route: {url}')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing arguments. Usage: !find_route <origin> <destination> <number_of_attractions> <travel_mode>')
    if isinstance(error, commands.CommandError):
        await ctx.send(error)
    if isinstance(error, commands.BadArgument):
        await ctx.send("The number of attractions parameter is not a number")

bot.run(discord_key)


