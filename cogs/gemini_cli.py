import discord
import subprocess
import os
from discord.ext import commands


class Gemini_cli(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="search", help="向 Gemini AI 提問。")
    async def search(self, ctx, *, prompt: str):
        """
        向 Gemini AI 提問。使用範例: Jarvis search 什麼是大型語言模型?
        """
        command = f'gemini -p "{prompt}"'
        try:
            # 顯示 "機器人正在輸入..."
            async with ctx.typing():
                # 發送請求到 Gemini API
                response = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True, 
                    encoding='utf-8', 
                    errors='replace', 
                    check=True,
                    timeout=300
                )
                
                # 檢查是否有回應內容
                if response.stdout:
                    for i in range(0, len(response.stdout), 2000):
                        await ctx.send(response.stdout[i:i+2000])
                else:
                    await ctx.send("很抱歉，我無法產生回應。")
        except Exception as e:
            await ctx.send(f"❌ 發生錯誤：{e}")

# Cog 的入口
async def setup(bot):
    await bot.add_cog(Gemini_cli(bot))
