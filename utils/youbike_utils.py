import requests
from difflib import get_close_matches

YOUBIKE_API_URL = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"

def fetch_youbike_data():
    """
    從 YouBike API 取得最新資料。
    """
    response = requests.get(YOUBIKE_API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("❌ 無法取得 YouBike 資料，請稍後再試。")

def fuzzy_match_station_name(name: str, station_data: list, n=1, cutoff=0.3):
    """
    用 difflib 模糊比對站名，回傳匹配的站點列表。
    """
    station_names = [s["sna"] for s in station_data]
    matches = get_close_matches(name, station_names, n=n, cutoff=cutoff)
    return [s for s in station_data if s["sna"] in matches]

def get_station_by_exact_name(name: str, station_data: list):
    """
    精確取得站點資料（已知站名時使用）。
    """
    return next((s for s in station_data if s["sna"] == name), None)