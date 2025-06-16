import asyncio
import csv
import sys
from pathlib import Path
from thread.scrape_thread import scrape_thread
from playwright.async_api import async_playwright

def clean_text(text: str) -> str:
    return " ".join(text.replace("\n", " ").split())

async def crawl_main_posts_from_lexicon(keyword: str):
    Path("data").mkdir(exist_ok=True)
    output_path = Path("data/main_posts.csv")
    seen_posts = set()
    symptom_group = "fatigue"
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        with open(output_path, "w", newline="", encoding="utf-8") as out_csv:
            writer = csv.writer(out_csv)
            writer.writerow(["username", "text", "timestamp", "url", "symptom_group", "keyword"])

            print(f"Tìm bài với từ khóa: {keyword}")
            try:
                await page.goto(f"https://www.threads.net/search?q={keyword}", timeout=45000)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)

                for _ in range(10):
                    await page.mouse.wheel(0, 1000)
                    await asyncio.sleep(2)

                from parsel import Selector
                html = await page.content()
                selector = Selector(text=html)
                posts = selector.css('a[href^="/@"][href*="/post/"]')
                print(f"  -> Tìm thấy {len(posts)} bài")

                for post in posts:
                    href = post.attrib['href']
                    if "/media" in href:
                        continue  
                    post_link = "https://www.threads.net" + href

                    try:
                        thread_data = await asyncio.to_thread(scrape_thread, post_link)
                        thread_main = thread_data.get("thread", {})
                        username = thread_main.get("username", "")
                        content = clean_text(thread_main.get("text", "") or "")
                        timestamp = thread_main.get("published_on", "") or ""
                    except Exception as e:
                        print(f"    Lỗi lấy thread chi tiết {post_link}: {e}")
                        continue

                    key = (username, content)
                    if content and username and key not in seen_posts:
                        writer.writerow([username, content, timestamp, post_link, symptom_group, keyword])
                        seen_posts.add(key)
            except Exception as e:
                print(f"Lỗi với từ khóa '{keyword}': {e}")

        await context.close()
        await browser.close()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python cre.py <keyword>")
        return
    keyword = sys.argv[1]
    await crawl_main_posts_from_lexicon(keyword)

if __name__ == "__main__":
    asyncio.run(main())
