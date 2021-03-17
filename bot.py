import sqlite3
import discord
from discord.ext import commands
import json
from geopy.geocoders import Nominatim
import weather

with open('secrets.json', 'r') as f:
    secrets = json.loads(f.read())
    TOKEN = secrets['BOT_TOKEN']

db_path = ('data.db')

bot = commands.Bot(command_prefix='f.')

@bot.event
async def on_ready():

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # create the guild table if its not already made
    c.execute('create table if not exists guilds (gid int primary key, lat string, lon string, prefix string);')

    conn.commit()
    conn.close()

    print(f'{bot.user} is in the house!!')

async def check_guild(gid):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # check if user already exists
    c.execute('select * from guilds where gid=?', (gid,))
    guild = c.fetchone()

    # if they dont, add them
    if (guild == None):
        c.execute('insert into guilds(gid, lat, lon, prefix) values(?,?,?,?)', (gid,"0","0","f!"))
        c.execute('select * from guilds where gid=?', (gid,))
        guild = c.fetchone()

    conn.commit()
    conn.close()

    return guild    

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

@bot.command()
async def frisbee(ctx, day='current'):

    guild = await check_guild(ctx.message.guild.id)

    if guild[1] == 0 or guild[2] == 0:
        await ctx.message.channel.send('latitude and/or longitude not set!')
        return

    await ctx.message.channel.send(weather.get_weather(guild[1], guild[2], day))

@bot.command()
async def setlocation(ctx, lat, lon):
    geolocator = Nominatim(user_agent="geoapiExercises")

    lat = lat.strip(',')

    try:
        location = geolocator.reverse(lat+","+lon)
    except:
        await ctx.message.channel.send('not valid coordinates')
        return

    if not location:
        await ctx.message.channel.send(f'location set to {lat}, {lon}')
    elif 'city' in location.raw["address"]:
        await ctx.message.channel.send(f'location set to {location.raw["address"]["city"]}')
    elif 'country' in location.raw["address"]:
        await ctx.message.channel.send(f'location set to {location.raw["address"]["country"]}')
    else:
        await ctx.message.channel.send(f'location set to {lat}, {lon}')

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # add coordinates to database
    c.execute('update guilds set lat=?,lon=? where gid=?', (lat, lon, ctx.guild.id))

    conn.commit()
    conn.close()

bot.run(TOKEN)
