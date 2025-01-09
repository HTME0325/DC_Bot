# 導入Discord.py模組
import discord
from discord.ext import commands
import configparser as cp
import re
import requests
from difflib import get_close_matches
from stock import get_stock_price

config_file = cp.ConfigParser()
config_file.read("../envs/config.ini")


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='Jarvis ', intents=intents)


@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello!, {ctx.author.name}!')


@bot.event
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")



YOUBIKE_API_URL = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"


@bot.command()
async def youbike(ctx, *, station_name: str):
    """
    查詢 YouBike 站點資訊，支援關鍵字模糊查詢。
    使用範例：Jarvis youbike 芝山
    """
    try:
        # 清理輸入的多餘空白
        station_name = ' '.join(station_name.split())
        
        # 從 API 獲取資料
        response = requests.get(YOUBIKE_API_URL)
        if response.status_code != 200:
            await ctx.send("❌ 無法取得 YouBike 資料，請稍後再試。")
            return

        youbike_data = response.json()

        # 提取所有站點名稱
        station_names = [station["sna"] for station in youbike_data]

        # 使用 difflib.get_close_matches 進行模糊匹配
        matched_stations = get_close_matches(station_name, station_names, n=5, cutoff=0.3)

        if matched_stations:
            results = []
            for name in matched_stations:
                # 找到完整的站點資料
                station_info = next((station for station in youbike_data if station["sna"] == name), None)
                if station_info:
                    results.append(f"🚲 **{station_info['sna']}**: 可租借 {station_info.get('available_rent_bikes', '未知')} 台。")
            # 回傳匹配結果
            await ctx.send("\n".join(results))
        else:
            await ctx.send(f"❌ 找不到與 **{station_name}** 相符的站點，請確認名稱是否正確。")
    except Exception as e:
        await ctx.send(f"❌ 查詢失敗，錯誤訊息：{e}")


@bot.command()
async def stock(ctx, *, stock_name: str):
    await ctx.send(get_stock_price(stock_name))




bot.run(f"{config_file["DC"]["token"]}")