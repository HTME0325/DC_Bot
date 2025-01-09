# 導入Discord.py模組
import discord
from discord.ext import commands
import configparser as cp
import re


#
config_file = cp.ConfigParser()
config_file.read("../envs/config.ini")

# client是跟discord連接，intents是要求機器人的權限
intents = discord.Intents.default()
intents.message_content = True
# bot = discord.Client(intents = intents)



#訊息開頭需是!
bot = commands.Bot(command_prefix='Jarvis ', intents=intents)


@bot.command()
async def userinfoo(ctx, member: commands.MemberConverter):
    roles = [role.name for role in member.roles[1:]]
    await ctx.send(
        f"User name: {member.name}\n"
        f"User ID: {member.id}\n"
        f"Joined at: {member.joined_at}\n" 
        f"Roles: {', '.join(roles)}"
    )



# @bot.command()  
# async def userinfo(ctx, user_mention):

#     user_id = re.search(r'\d+', user_mention).group()
  
#     user = await bot.fetch_user(user_id)
  

#     await ctx.send(f"User name: {user.name}, ID: {user.id}")


@bot.command()  
async def userinfo(ctx, user_mention):

    user_id = re.search(r'\d+', user_mention).group()
  
    user = await bot.fetch_user(user_id)
    guild = ctx.guild
    member = await guild.fetch_member(user_id)
    roles = member.roles
    roles = roles[1:]  
    joined_at = member.joined_at


    await ctx.send(f"User name: {user.name}\n"
                    f"ID: {user.id}\n"
                    f"Join time: {joined_at}\n"
                    f"Roles: {[r.name for r in roles]}\n")

@bot.command()
async def getguild(ctx):
    await ctx.send(f'guild id: {ctx.guild.id}')


@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello!, {ctx.author.name}!')

# 調用event函式庫
@bot.event
# 當機器人完成啟動
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")
       

bot.run(f"{config_file["DC"]["token"]}")