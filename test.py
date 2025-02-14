import os
NOTION_API_KEY = os.getenv("NOTION_API_KEY")  # 這樣 GitHub Actions 會自動讀取金鑰

import requests
import json
from datetime import datetime

# ✅ 設定 Notion API 金鑰 & 資料庫 ID
DATABASE_ID = "197cc8ff5d1c80f08a8cc2e28a1e2ab3"

import feedparser  # 需要安裝 feedparser 套件
import urllib.parse
from datetime import datetime

# ✅ API 端點（確保 DATABASE_ID 正確）
url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"


# ✅ 設定請求標頭
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json; charset=utf-8",
    "Notion-Version": "2022-06-28",
    "Accept-Charset": "utf-8"
}

# ✅ 設定你要查詢的公司（台灣 + 國外）
COMPANIES = ["Tesla", "Apple", "Microsoft", "Nvidia", "Amazon", "台積電", "鴻海", "聯發科", "長榮海運", "大立光"]


# ✅ 產生 Google News RSS 搜尋 URL
query = " OR ".join(COMPANIES)  # 讓 Google News RSS 搜尋這些關鍵字
encoded_query = urllib.parse.quote(query)  # 轉換成 URL 可用格式
NEWS_FEED_URL = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"

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

# ✅ 取得當天日期（格式：YYYY-MM-DD）
today_date = datetime.now().strftime("%Y-%m-%d")

# ✅ 解析 RSS，篩選出「當天新聞」
def get_today_news():
    feed = feedparser.parse(NEWS_FEED_URL)
    today_news = []
    
    for entry in feed.entries:
        # 🟢 確保 `published_parsed` 正確解析時間
            if hasattr(entry, 'published_parsed'):
                news_date = datetime(*entry.published_parsed[:3]).strftime("%Y-%m-%d")
            
            if news_date == today_date:  # 只抓當天的新聞
                today_news.append({
                    "title": entry.title,
                    "url": entry.link,
                    "date": news_date
                })

    print(f"📅 今日篩選後的新聞數量：{len(today_news)}")  # Debug
    return today_news

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

news_list = get_today_news()

if news_list:
    print(f"✅ 今天有 {len(news_list)} 則新聞，開始寫入 Notion...")
    for news in news_list:
        print(f"✅ 成功新增新聞：{news['title']}")
else:
    print("🚫 今天沒有新聞，不寫入 Notion")
