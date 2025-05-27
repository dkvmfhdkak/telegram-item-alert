import os, json, requests, schedule, time
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.constants import ParseMode

TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID    = os.getenv("CHAT_ID")
KEYWORDS   = ["썬콜","불독","클레릭","비숍"]
MAX_PRICE  = 1_000_000
SEEN_FILE  = "seen.json"
bot = Bot(token=TELE_TOKEN)

def load_seen():
    try:
        return set(json.load(open(SEEN_FILE, "r", encoding="utf8")))
    except:
        return set()

def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf8") as f:
        json.dump(list(seen), f, ensure_ascii=False, indent=2)

def send(msg):
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode=ParseMode.HTML)

def check_itemmania_other(seen):
    url = "https://www.itemmania.com/maplestory/other_char_search.php?keyword=" + "+".join(KEYWORDS)
    soup = BeautifulSoup(requests.get(url, headers={"User-Agent":"Mozilla/5.0"}).text, "lxml")
    for item in soup.select(".list-item"):
        pid   = item.get("data-id")
        title = item.select_one(".title").get_text(strip=True)
        price = int(item.select_one(".price").get_text().replace(",", ""))
        link  = "https://www.itemmania.com" + item.select_one("a")["href"]
        if price < MAX_PRICE and any(k in title for k in KEYWORDS) and pid not in seen:
            seen.add(pid)
            send(f"[ItemMania 기타] <a href=\"{link}\">{title}</a> — {price}원")

def check_itemmania_world(seen):
    url = "https://www.itemmania.com/maplestoryworld/mapleland_char_search.php?keyword=" + "+".join(KEYWORDS)
    soup = BeautifulSoup(requests.get(url, headers={"User-Agent":"Mozilla/5.0"}).text, "lxml")
    for item in soup.select(".list-item"):
        pid   = item.get("data-id")
        title = item.select_one(".title").get_text(strip=True)
        price = int(item.select_one(".price").get_text().replace(",", ""))
        link  = "https://www.itemmania.com" + item.select_one("a")["href"]
        if price < MAX_PRICE and any(k in title for k in KEYWORDS) and pid not in seen:
            seen.add(pid)
            send(f"[ItemMania 월드] <a href=\"{link}\">{title}</a> — {price}원")

def check_barotem(seen):
    url = ("https://www.barotem.com/search?"
           "game=메이플스토리&world=메이플월드&type=sell"
           "&keyword=" + "+".join(KEYWORDS))
    soup = BeautifulSoup(requests.get(url, headers={"User-Agent":"Mozilla/5.0"}).text, "lxml")
    for item in soup.select(".item-list .item"):
        pid   = item.get("data-id")
        title = item.select_one(".item-title").get_text(strip=True)
        price = int(item.select_one(".item-price").get_text().replace(",", ""))
        link  = "https://www.barotem.com" + item.select_one("a")["href"]
        if price < MAX_PRICE and any(k in title for k in KEYWORDS) and pid not in seen:
            seen.add(pid)
            send(f"[바로템] <a href=\"{link}\">{title}</a> — {price}원")

def job():
    seen = load_seen()
    check_itemmania_other(seen)
    check_itemmania_world(seen)
    check_barotem(seen)
    save_seen(seen)

if __name__ == "__main__":
    job()
    schedule.every(5).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
