# DC_Bot

# 🚴 YouBike 通勤助手 Bot

一個支援 YouBike 即時站點查詢、模糊搜尋、與通勤距離估算的 Discord Bot。支援互動式選單、Google Maps 開啟導航，並整合 OpenRouteService 預估實際騎乘距離與時間。

---

## ✨ 功能特色

- 🔍 模糊搜尋 YouBike 站點
- 📍 顯示站點目前可借與可停資訊
- 🚴 通勤估算（直線距離 + 騎乘路徑）
- 📊 Google Maps 導航連結
- 🧠 互動式下拉選單選擇起訖站
- 🗺️ 使用 OpenRouteService 預估實際距離與時間

---

## ⚙️ 安裝與執行方式

### 1. 安裝依賴
```bash
pip install -r requirements.txt
```


### 2. 建立.env
建立範例：

DC_token = "your token"

ORS_key = "your API key"

請先到discord申請自己的token https://discord.com/developers/docs/reference
以及到openrouteservice申請api金鑰 https://openrouteservice.org/


### 3. 執行 bot
```
python bot.py
```

## 🔐 使用 API 與授權

### OpenRouteService (ORS)
* 用於預估騎乘時間與實際距離

### YouBike 即時資料
* 政府開放資料平台（例如台北市資料大平台）

### Google Maps
* 僅用於產生導航連結，未使用其 API


