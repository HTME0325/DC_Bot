import requests
import configparser as cp

config_file = cp.ConfigParser()
config_file.read("envs/config.ini")

ORS_API_KEY = config_file["ORS"]["ORS_key"] 

def get_route_info(from_coord, to_coord):
    """
    傳入經緯度座標（(lat, lon)），回傳 (距離_km, 時間_min)
    """
    url = "https://api.openrouteservice.org/v2/directions/cycling-regular"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            [from_coord[1], from_coord[0]],  # 注意順序是 [lon, lat]
            [to_coord[1], to_coord[0]]
        ]
    }

    try:
        res = requests.post(url, json=body, headers=headers)
        res.raise_for_status()

        # ❗ 顯示錯誤內容
        if res.status_code != 200:
            print(f"❌ ORS 錯誤狀態碼: {res.status_code}")
            print(f"❌ 錯誤內容: {res.text}")
            return None, None


        data = res.json()


        # ✔️ 使用新版格式中的 routes
        if "routes" not in data or not data["routes"]:
            print(f"⚠️ ORS 回傳格式不正確: {data}")
            return None, None


        segment = data["routes"][0]["segments"][0]
        distance_km = segment["distance"] / 1000
        duration_min = segment["duration"] / 60

        return round(distance_km, 2), round(duration_min, 1)

    except Exception as e:
        print(f"🚨 ORS API 錯誤：{e}")
        return None, None
