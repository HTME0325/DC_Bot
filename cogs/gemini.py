import os
from discord.ext import commands
import google.generativeai as genai
from dotenv import load_dotenv

# --- 初始化設定 ---

# 讀取 .env 檔案中的環境變數
load_dotenv()

# 從環境變數取得 API 金鑰並設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("未找到 GEMINI_API_KEY，請在 .env 檔案中設定。")

genai.configure(api_key=GEMINI_API_KEY)

# --- Gemini Cog ---

class Gemini(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 選擇要使用的模型
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    @commands.command(name="ask", help="向 Gemini AI 提問。")
    async def ask(self, ctx, *, prompt: str):
        """
        向 Gemini AI 提問。使用範例: Jarvis ask 什麼是大型語言模型?
        """
        try:
            # 顯示 "機器人正在輸入..."
            async with ctx.typing():
                # 發送請求到 Gemini API
                response = await self.model.generate_content_async(prompt)
                
                # 檢查是否有回應內容
                if response.text:
                    await ctx.send(response.text)
                else:
                    await ctx.send("很抱歉，我無法產生回應。")
        except Exception as e:
            await ctx.send(f"❌ 發生錯誤：{e}")

# Cog 的入口
async def setup(bot):
    await bot.add_cog(Gemini(bot))

