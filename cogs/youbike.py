from discord.ext import commands
from discord import Interaction, SelectOption, Embed
from discord.ui import View, Select
import requests
from difflib import get_close_matches
from geopy.distance import geodesic


YOUBIKE_API_URL = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
E_BIKE_API = "https://apis.youbike.com.tw/api/front/bike/lists?station_no={}"

def fetch_ebike_info(station_no):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }
        res = requests.get(E_BIKE_API.format(station_no), headers=headers)
        data = res.json()
        if data.get("retCode") == 1:
            return data["retVal"]
        return []
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return []


class StationSelect(Select):
    def __init__(self, stations, youbike_data):
        self.youbike_data = youbike_data
        options = [SelectOption(label=station, value=station) for station in stations]
        super().__init__(placeholder="請選擇正確的站點...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction):
        selected_station = self.values[0]
        station_info = next((s for s in self.youbike_data if s["sna"] == selected_station), None)

        if station_info:
            embed = Embed(title=f"🚲 {station_info['sna']}", color=0x4CAF50)
            embed.add_field(name="🔓 可租借", value=f"{station_info.get('available_rent_bikes', '未知')} 台", inline=True)
            embed.add_field(name="🔒 可停空位", value=f"{station_info.get('available_return_bikes', '未知')} 台", inline=True)
            
            # 🔋 E-Bike info
            ebike_info = fetch_ebike_info(station_info["sno"])
            if ebike_info:
                ebike_str = '\n'.join(
                    f"🔋 車號：{bike['bike_no']}（電量：{bike['battery_power']}%）"
                    for bike in ebike_info
                )
                embed.add_field(name="⚡ E-Bike 資訊", value=ebike_str, inline=False)

            embed.add_field(name="🔄 更新時間", value=station_info.get("mday", "未知"), inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("❌ 找不到該站點的詳細資料", ephemeral=True)


class StationSelectView(View):
    def __init__(self, stations, youbike_data):
        super().__init__(timeout=30)
        self.add_item(StationSelect(stations, youbike_data))


class YouBike(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def youbike(self, ctx, *, station_name: str):
        """
        查詢 YouBike 站點資訊，支援關鍵字模糊查詢並支援互動式選擇。
        使用範例：Jarvis youbike 芝山
        """
        try:
            station_name = ' '.join(station_name.split())
            response = requests.get(YOUBIKE_API_URL)
            if response.status_code != 200:
                await ctx.send("❌ 無法取得 YouBike 資料，請稍後再試。")
                return

            youbike_data = response.json()
            station_names = [station["sna"] for station in youbike_data]
            matched_stations = get_close_matches(station_name, station_names, n=5, cutoff=0.3)

            if len(matched_stations) == 0:
                await ctx.send(f"❌ 找不到與 **{station_name}** 相符的站點，請確認名稱是否正確。")
            elif len(matched_stations) == 1:
                # 只有一個結果就直接顯示
                selected = matched_stations[0]
                station_info = next((s for s in youbike_data if s["sna"] == selected), None)
                if station_info:
                    embed = Embed(title=f"🚲 {station_info['sna']}", color=0x4CAF50)
                    embed.add_field(name="🔓 可租借", value=f"{station_info.get('available_rent_bikes', '未知')} 台", inline=True)
                    embed.add_field(name="🔒 可停空位", value=f"{station_info.get('available_return_bikes', '未知')} 台", inline=True)
                     
                     # 🔋 E-Bike info
                    ebike_info = fetch_ebike_info(station_info["sno"])
                    if ebike_info:
                        ebike_str = '\n'.join(
                            f"🔋 車號：{bike['bike_no']}（電量：{bike['battery_power']}%）"
                            for bike in ebike_info
                        )
                        embed.add_field(name="⚡ E-Bike 資訊", value=ebike_str, inline=False)

                    embed.add_field(name="🔄 更新時間", value=station_info.get("mday", "未知"), inline=False)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ 找不到該站點的詳細資料。")
            else:
                # 多個選項時顯示互動式選單
                view = StationSelectView(matched_stations, youbike_data)
                await ctx.send("🔍 找到多個相似站點，請從下拉選單中選擇：", view=view)

        except Exception as e:
            await ctx.send(f"❌ 查詢失敗，錯誤訊息：{e}")


# Cog 的入口
async def setup(bot):
    await bot.add_cog(YouBike(bot))
