from difflib import get_close_matches


# 🧠 共用函式：模糊找站點
def fuzzy_find_matches(name, station_data, limit=5):
    station_names = [s["sna"] for s in station_data]
    return get_close_matches(name, station_names, n=limit, cutoff=0.3)

# 🧠 共用函式：找站點資料
def get_station_by_name(name, station_data):
    return next((s for s in station_data if s["sna"] == name), None)