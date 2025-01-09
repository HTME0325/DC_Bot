import requests
from bs4 import BeautifulSoup

def get_stock_price(stock_symbol):
    """
    從 Yahoo 股票頁面提取指定股票的股價。
    
    :param stock_symbol: 股票代碼（例如 "2330.TW"）
    :return: 股票名稱與股價，若失敗則返回錯誤訊息
    """
    try:
        # Yahoo 股票頁面 URL
        url = f"https://tw.stock.yahoo.com/quote/{stock_symbol}"
        
        # 發送請求取得網頁內容
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 確保請求成功

        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 定位股價元素
        price_span = soup.find('span', class_="Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c)")
        
        if price_span:
            stock_price = price_span.text
            return f"股票 {stock_symbol} 的目前價格為: {stock_price} 元"
        else:
            return f"無法從 Yahoo 股票頁面提取 {stock_symbol} 的價格，請檢查代碼是否正確。"
    except Exception as e:
        return f"查詢失敗，錯誤訊息: {e}"

