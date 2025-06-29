import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()


intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"✅ 已載入擴充模組: {filename}")
                except Exception as e:
                    print(f"❌ 無法載入擴充模組 {filename}: {e}")

bot = MyBot(command_prefix='Jarvis ', intents=intents)

@bot.event
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")

bot.run(os.getenv("DC_token"))
