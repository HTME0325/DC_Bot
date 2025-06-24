from discord.ext import commands
from discord import Interaction, SelectOption, Embed
from discord.ui import View, Select, Button
from discord import ButtonStyle
import requests
from difflib import get_close_matches
from geopy.distance import geodesic
from utils.youbike_utils import fuzzy_find_matches, get_station_by_name
from utils.get_route_info import get_route_info



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


    @commands.command()
    async def commute(self, ctx, *, text: str):
        """
        通勤距離估算：格式 `地點A 到 地點B`，支援模糊比對與互動式選擇。
        """
        try:
            if "到" not in text:
                await ctx.send("⚠️ 請使用格式：`地點A 到 地點B`（中間要有「到」）")
                return

            from_input, to_input = [s.strip() for s in text.split("到")]

            res = requests.get(YOUBIKE_API_URL)
            if res.status_code != 200:
                await ctx.send("❌ 無法取得資料")
                return

            station_data = res.json()
            from_matches = fuzzy_find_matches(from_input, station_data)
            to_matches = fuzzy_find_matches(to_input, station_data)

            if not from_matches or not to_matches:
                await ctx.send("❌ 找不到起點或終點，請確認名稱")
                return

            if len(from_matches) == 1 and len(to_matches) == 1:
                # ✅ 直接顯示結果
                from_station = get_station_by_name(from_matches[0], station_data)
                to_station = get_station_by_name(to_matches[0], station_data)

                from_coord = (float(from_station["latitude"]), float(from_station["longitude"]))
                to_coord = (float(to_station["latitude"]), float(to_station["longitude"]))
                route_distance_km, route_duration_min = get_route_info(from_coord, to_coord)
                google_maps_url = (
                    f"https://www.google.com/maps/dir/?api=1"
                    f"&origin={from_coord[0]},{from_coord[1]}"
                    f"&destination={to_coord[0]},{to_coord[1]}"
                    f"&travelmode=bicycling"
                )

                # distance_km = geodesic(from_coord, to_coord).km

                embed = Embed(title="🚴 通勤估算", color=0x03A9F4)
                embed.add_field(name="📍 起點站", value=from_station["sna"], inline=False)
                embed.add_field(name="🔓 可租車輛", value=f"{from_station.get('available_rent_bikes', '未知')} 台", inline=True)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name="🏁 終點站", value=to_station["sna"], inline=False)
                embed.add_field(name="🔒 可停空位", value=f"{to_station.get('available_return_bikes', '未知')} 台", inline=True)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name="🗺️ 地圖與路線", value=f"[在 Google Maps 上查看]({google_maps_url})", inline=False)
                # embed.add_field(name="📏 直線距離", value=f"{distance_km:.2f} 公里", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name="🛣️ 實際路徑距離", value=f"{route_distance_km:.2f} 公里", inline=False)
                embed.add_field(name="⏱️ 預估時間", value=f"{route_duration_min:.1f} 分鐘", inline=False)
                embed.add_field(name="📎 資料來源", value="路線預估由 [OpenRouteService](https://openrouteservice.org) 提供", inline=False)


                await ctx.send(embed=embed)
            else:
                # 🤖 多個結果，用互動選擇
                view = CommuteSelectView(from_matches, to_matches, station_data)
                await ctx.send("🔍 找到多個相似站點，請從下拉選單中選擇：", view=view)

        except Exception as e:
            await ctx.send(f"❌ 發生錯誤：{e}")


class CommuteSelect(Select):
    def __init__(self, role, options, station_data, parent_view):
        self.role = role
        self.station_data = station_data
        self.parent_view = parent_view
        select_options = [SelectOption(label=name, value=name) for name in options]
        placeholder = "選擇起點" if role == "from" else "選擇終點"
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=select_options)

    async def callback(self, interaction: Interaction):
        selected_name = self.values[0]
        station = get_station_by_name(selected_name, self.station_data)
        if self.role == "from":
            self.parent_view.from_station = station
        else:
            self.parent_view.to_station = station

        await interaction.response.send_message(f"✅ 已選擇 {self.role}：{selected_name}，請繼續操作", ephemeral=True)

class CommuteSelectView(View):
    def __init__(self, from_options, to_options, station_data):
        super().__init__(timeout=60)
        self.station_data = station_data
        self.from_station = None
        self.to_station = None

        self.from_select = CommuteSelect("from", from_options, station_data, self)
        self.to_select = CommuteSelect("to", to_options, station_data, self)
        self.add_item(self.from_select)
        self.add_item(self.to_select)

        self.submit_button = Button(label="送出", style=ButtonStyle.primary)
        self.submit_button.callback = self.on_submit
        self.add_item(self.submit_button)

    async def on_submit(self, interaction: Interaction):
        if not self.from_station or not self.to_station:
            await interaction.response.send_message("⚠️ 請確認已選擇起點與終點", ephemeral=True)
            return

        try:
            from_coord = (float(self.from_station["latitude"]), float(self.from_station["longitude"]))
            to_coord = (float(self.to_station["latitude"]), float(self.to_station["longitude"]))

            route_distance_km, route_duration_min = get_route_info(from_coord, to_coord)
            google_maps_url = (
                f"https://www.google.com/maps/dir/?api=1"
                f"&origin={from_coord[0]},{from_coord[1]}"
                f"&destination={to_coord[0]},{to_coord[1]}"
                f"&travelmode=bicycling"
            )
            # distance_km = geodesic(from_coord, to_coord).km

            embed = Embed(title="🚴 通勤估算", color=0x03A9F4)
            embed.add_field(name="📍 起點站", value=self.from_station["sna"], inline=False)
            embed.add_field(name="🔓 可租車輛", value=f"{self.from_station.get('available_rent_bikes', '未知')} 台", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=False)
            embed.add_field(name="🏁 終點站", value=self.to_station["sna"], inline=False)
            embed.add_field(name="🔒 可停空位", value=f"{self.to_station.get('available_return_bikes', '未知')} 台", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=False)
            embed.add_field(name="🗺️ 地圖與路線", value=f"[在 Google Maps 上查看]({google_maps_url})", inline=False)
            # embed.add_field(name="📏 直線距離", value=f"{distance_km:.2f} 公里", inline=False)
            embed.add_field(name="\u200b", value="\u200b", inline=False)
            embed.add_field(name="🛣️ 實際路徑距離", value=f"{route_distance_km:.2f} 公里", inline=False)
            embed.add_field(name="⏱️ 預估時間", value=f"{route_duration_min:.1f} 分鐘", inline=False)
            embed.add_field(name="📎 資料來源", value="路線預估由 [OpenRouteService](https://openrouteservice.org) 提供", inline=False)


            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ 計算錯誤：{e}", ephemeral=True)


# Cog 的入口
async def setup(bot):
    await bot.add_cog(YouBike(bot))
