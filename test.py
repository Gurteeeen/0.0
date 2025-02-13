import os
NOTION_API_KEY = os.getenv("NOTION_API_KEY")  # 這樣 GitHub Actions 會自動讀取金鑰

import requests
import json

# ✅ 設定 Notion API 金鑰 & 修正 `DATABASE_ID`  # 請確保這裡是正確的金鑰
DATABASE_ID = "197cc8ff5d1c80f08a8cc2e28a1e2ab3"  # ✅ 這裡應該是純 ID，不是完整網址

# ✅ 設定請求標頭
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# ✅ API 端點（確保 DATABASE_ID 正確）
url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"

# ✅ 發送請求到 Notion API
response = requests.get(url, headers=headers)

# ✅ 確認 response 是否有正確回應
if response.status_code == 200:
    print(json.dumps(response.json(), indent=4, ensure_ascii=False))  # 美化輸出 JSON 結果
else:
    print(f"❌ 請求失敗，狀態碼: {response.status_code}")
    print(response.text)  # 印出 API 回應內容，找出錯誤原因

def add_news_to_notion(title, url, date):
    notion_url = "https://api.notion.com/v1/pages"
    
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {  # 這裡應該對應 Notion 的標題欄位
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
                "Task": { "select": { "name": "Onboarding Flow" } }, # Task 是文字欄位，不是 URL
            "Date": { "date": { "start": date } } , # Date 應該是日期欄位
            "URL": { "url": url }
        }
    }

    response = requests.post(notion_url, headers=headers, json=data)
    return response.status_code, response.json()
 




# ✅ 測試寫入 Notion
news_title = "特朗普光環失效？Tesla暴跌原因剖釋"
news_url = "https://hk.finance.yahoo.com/news/%E7%89%B9%E6%9C%97%E6%99%AE%E5%85%89%E7%92%B0%E5%A4%B1%E6%95%88%EF%BC%9Ftesla%E6%9A%B4%E8%B7%8C%E5%8E%9F%E5%9B%A0%E5%89%96%E9%87%8B-054118450.html?guccounter=1&guce_referrer=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8&guce_referrer_sig=AQAAAHSf5Jzoc3-aN_sN3pookRLoE9BkFAHqJwej62DzazFc0lRJ3LwHj96tCTMeKLdwQ89siRMLcDAPpYa6k3wcxT3UOgyy5LiKX5oVWm0o3QR5JC-1-bKYvN78EI1ZLlQkGMqzb2IhIoPDLBA8Frm3cHHeN__TCQRuxL5L_xpxCRS6"
news_date = "2025-02-12"

status, result = add_news_to_notion(news_title, news_url, news_date)

# ✅ 顯示 Notion API 回應結果
print("📌 API 回應 JSON：")
print(result)
import requests
import json
import feedparser  # 需要安裝 feedparser 套件
from datetime import datetime

# ✅ 設定 Notion API 金鑰 & 資料庫 ID
DATABASE_ID = "197cc8ff5d1c80f08a8cc2e28a1e2ab3"

# ✅ 設定請求標頭
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
    "Accept-Charset": "utf-8"
}

# ✅ Google News RSS URL（Tesla 股票新聞）
GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search?q=Tesla+stock&hl=en-US&gl=US&ceid=US:en"

# ✅ 解析 Google News RSS
def fetch_google_news():
    news_feed = feedparser.parse(GOOGLE_NEWS_RSS_URL)
    news_list = []
    
    for entry in news_feed.entries[:1]:  # 限制抓取 5 則新聞
        title = entry.title
        link = entry.link
        published_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d")
        
        news_list.append({"title": title, "url": link, "date": published_date})
    
    return news_list

# ✅ 新增新聞到 Notion
def add_news_to_notion(title, url, date):
    notion_url = "https://api.notion.com/v1/pages"
    
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {  
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            "Task": { "select": { "name": "Onboarding Flow" } },  # ✅ Task 選擇欄位
            "Date": { "date": { "start": date } },  # ✅ 日期欄位
            "URL": { "url": url }  # ✅ 確保這裡是正確的 URL 欄位名稱
        }
    }

# ✅ 自動化流程（Google News）
news_list = fetch_google_news()

for news in news_list:
    add_news_to_notion(news["title"], news["url"], news["date"])

import requests
import json
import feedparser  # 需要安裝 feedparser 套件
import urllib.parse
from datetime import datetime



# ✅ 設定請求標頭
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json; charset=utf-8",
    "Notion-Version": "2022-06-28",
    "Accept-Charset": "utf-8"
}

# ✅ 設定你要查詢的公司（台灣 + 國外）
COMPANIES = ["Tesla", "Apple", "Microsoft", "Nvidia", "Amazon", "台積電", "鴻海", "聯發科", "長榮海運", "大立光"]

# ✅ 解析 Google News RSS
def fetch_google_news(company):
    encoded_company = urllib.parse.quote(company, safe="", encoding="utf-8")  # ✅ 強制使用 UTF-8
    if company in ["台積電", "鴻海", "聯發科", "長榮海運", "大立光"]:
        rss_url = f"https://news.google.com/rss/search?q={encoded_company}+股價&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    else:
        rss_url = f"https://news.google.com/rss/search?q={encoded_company}+stock&hl=en-US&gl=US&ceid=US:en"
    
    news_feed = feedparser.parse(rss_url)
    news_list = []
    
    for entry in news_feed.entries[:1]:  # 限制抓取 5 則新聞
        title = entry.title.encode("utf-8", "ignore").decode("utf-8")  # ✅ 強制 UTF-8
        link = entry.link.encode("utf-8", "ignore").decode("utf-8")  # ✅ 確保 URL 正確
        published_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d")
        
        news_list.append({"title": title, "url": link, "date": published_date, "company": company})
    for news in news_list:
         print(news["title"], news["url"], news["date"])

    return news_list

# ✅ 新增新聞到 Notion
def add_news_to_notion(title, url, date):
    notion_url = "https://api.notion.com/v1/pages"
    
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {  
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            "Task": { "select": { "name": "Onboarding Flow" } },  # ✅ Task 選擇欄位
            "Date": { "date": { "start": date } },  # ✅ 日期欄位
            "URL": { "url": url }  # ✅ 確保這裡是正確的 URL 欄位名稱
        }
    }

    response = requests.post(notion_url, headers=headers, json=data)  # ✅ 使用 `json=data`

    if response.status_code == 200:
        print(f"✅ 成功新增新聞: {title}")
    else:
        print(f"❌ 新增新聞失敗: {title}，錯誤碼: {response.status_code}")
        print("🔹 API 回應內容：", response.text.encode("utf-8", "ignore").decode("utf-8"))

# ✅ 抓取多家公司新聞並寫入 Notion
for company in COMPANIES:
    news_list = fetch_google_news(company)
    for news in news_list:
        add_news_to_notion(news["title"], news["url"], news["date"])
for news in news_list:
     print(news["title"], news["url"], news["date"])
