import os
import json
from typing import Dict

import jmespath
from parsel import Selector
from playwright.sync_api import sync_playwright
from nested_lookup import nested_lookup

# Note: we'll also be using parse_thread function we wrote earlier:
from scrape_thread import parse_thread

def parse_profile(data: Dict) -> Dict:
    """Parse Threads profile JSON dataset for the most important fields"""
    result = jmespath.search(
        """{
        is_private: text_post_app_is_private,
        is_verified: is_verified,
        profile_pic: hd_profile_pic_versions[-1].url,
        username: username,
        full_name: full_name,
        bio: biography,
        bio_links: bio_links[].url,
        followers: follower_count
    }""",
        data,
    )
    result["url"] = f"https://www.threads.net/@{result['username']}"
    return result



def scrape_profile(url: str) -> dict:
    """Scrape Threads profile and their recent posts from a given URL"""
    with sync_playwright() as pw:
        # start Playwright browser
        browser = pw.chromium.launch()
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        page.goto(url)
        # wait for page to finish loading
        page.wait_for_selector("[data-pressable-container=true]")
        selector = Selector(page.content())
    parsed = {
        "user": {},
        "threads": [],
    }
    # find all hidden datasets
    hidden_datasets = selector.css('script[type="application/json"][data-sjs]::text').getall()
    for hidden_dataset in hidden_datasets:
        # skip loading datasets that clearly don't contain threads data
        if '"ScheduledServerJS"' not in hidden_dataset:
            continue
        is_profile = 'follower_count' in hidden_dataset
        is_threads = 'thread_items' in hidden_dataset
        if not is_profile and not is_threads:
            continue
        data = json.loads(hidden_dataset)
        if is_profile:
            user_data = nested_lookup('user', data)
            parsed['user'] = parse_profile(user_data[0])
        if is_threads:
            thread_items = nested_lookup('thread_items', data)
            threads = [
                parse_thread(t) for thread in thread_items for t in thread
            ]
            parsed['threads'].extend(threads)
    return parsed

if __name__ == "__main__":
    data = scrape_profile("https://www.threads.net/@natgeo")
    print(json.dumps(data, indent=2, ensure_ascii=False))
