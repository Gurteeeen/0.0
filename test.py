import os
NOTION_API_KEY = os.getenv("NOTION_API_KEY")  # 這樣 GitHub Actions 會自動讀取金鑰

import requests
import json
from datetime import datetime
import urllib.parse

# ✅ 設定 Notion API 金鑰 & 資料庫 ID
DATABASE_ID = "197cc8ff5d1c80f08a8cc2e28a1e2ab3"

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1340390610627989584/Mn94r688fJHn-YU5za1_t0XhjrCsWF8x-eukAOdF6PRFtpjfQioZxE2G-_ZU1mIIkXtY"

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
    company_news_count = {company: 0 for company in COMPANIES}
    seen_news = set()  # 🔹 存放 (標題, URL) 來過濾重複新聞

    for company in COMPANIES:  
        feed = feedparser.parse(NEWS_FEED_URL.format(company=company))

        for entry in feed.entries:
            # **如果新聞沒有日期，直接跳過**
            if "published_parsed" not in entry:
                continue
                
                news_date = datetime(*entry.published_parsed[:3]).strftime("%Y-%m-%d")
                
    for entry in feed.entries:
        # 🟢 確保 `published_parsed` 正確解析時間
            if hasattr(entry, 'published_parsed'):
                news_date = datetime(*entry.published_parsed[:3]).strftime("%Y-%m-%d")
            
            if news_date == today_date:  # 只抓當天的新聞
                for company in COMPANIES:
                    if company in entry.title and company_news_count[company] < 2:
                        today_news.append({
                            "title": entry.title,
                            "url": entry.link,
                            "date": news_date
                        })
                        
    for company in COMPANIES:    
            feed = feedparser.parse(NEWS_FEED_URL.format(company=company))
            seen_media = set()  # 記錄「已處理過的新聞媒體」

            for entry in feed.entries:
                news_date = datetime(*entry.published_parsed[:3]).strftime("%Y-%m-%d")
            
                if news_date == today_date:    
                    media_name = entry.source.title if "source" in entry else "Unknown"  # 獲取新聞媒體名稱
                    news_key = f"{company}-{media_name}"  # 建立唯一鍵值
                 
                    if news_key not in seen_media:  # 如果這個新聞媒體沒被處理過
                        today_news.append({
                            "company": company,
                            "media": media_name,
                            "title": entry.title,
                            "url": entry.link,
                            "date": news_date
                         })
                        seen_media.add(news_key)   # 標記為已處理

                        company_news_count[company] += 1
                        break  # 防止一篇新聞被記錄多

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
    try:
        response = requests.post(notion_url, headers=headers, json=data)
        response.raise_for_status()  # 若 API 回傳錯誤碼 (如 400/500) 會自動拋出例外

        # ✅ 送 Discord Webhook 通知
        send_discord_notification(title, url)

        return response.status_code, response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 新增新聞失敗：{title}")
        print(f"🔴 錯誤訊息：{e}")
        return None, None  # 避免程式崩潰

# ✅ 發送新聞到 Discord
def send_discord_notification(title, url):
    message = {
        "content": f"📢 **{title}**\n🔗 {url}"
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=message)
    if response.status_code == 204:
        print(f"✅ 已發送新聞到 Discord：{title}")
    else:
        print(f"❌ Discord 發送失敗，狀態碼：{response.status_code}")
    response = requests.post(DISCORD_WEBHOOK_URL, headers=headers, json=message)  # ✅ 使用 `json=data`

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
