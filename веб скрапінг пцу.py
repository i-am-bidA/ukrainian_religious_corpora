import requests
from bs4 import BeautifulSoup
import time
import re

BASE_URL = "https://www.pomisna.info/uk/category/vsi-novyny/page/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def get_full_article_text(url):
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            return "[Не вдалося завантажити текст статті]"
        soup = BeautifulSoup(res.content, "html.parser")
        article_block = soup.find("article", class_="article-item post-content page-content")
        if not article_block:
            return "[Текст відсутній]"
        text = article_block.get_text(separator=" ", strip=True)
        text = re.sub(r"\s{2,}", " ", text)
        return text
    except Exception as e:
        return f"[Помилка при завантаженні: {e}]"

def fetch_filtered_news():
    articles = []
    skip_phrases = ["Проповідь Блаженнійшого Митрополита", "Проповідь предстоятеля"]
    
    for page in range(1, 307):  # перші 100 сторінок категорії "Новини"
        url = f"{BASE_URL}{page}/"
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            print(f"❌ Помилка при зверненні до сторінки {page}")
            continue

        soup = BeautifulSoup(res.content, "html.parser")
        posts = soup.find_all("article", class_="article-item")
        print(f"Page {page} | Posts found: {len(posts)}")

        for post in posts:
            date_tag = post.find("div", class_="date-item")
            title_tag = post.find("h3")
            link_tag = title_tag.find("a") if title_tag else None

            if not date_tag or not link_tag:
                continue

            date_text = date_tag.get_text(strip=True)
            title = link_tag.get_text(strip=True)

            # Пропуск новин за фразами
            if any(phrase.lower() in title.lower() for phrase in skip_phrases):
                continue

            link = link_tag["href"]
            full_text = get_full_article_text(link)
            articles.append(f"{date_text} — {title}\n{full_text}\n\n")

            time.sleep(0.5)  # щоб не перевантажити сервер

    return articles

news_articles = fetch_filtered_news()

output_path = "1пцу_новини_проповіді.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.writelines(news_articles)
