import sys
import os
import csv
import json
import time
import asyncio
from datetime import datetime

def crawl_single_user_history(username):
    """Crawl history for a single user and append to CSV"""
    try:
        print(f"[DEBUG] Starting crawl for user: {username}")
        
        # Try to import scrape_profile
        try:
            from thread.scrape_profile import scrape_profile
            print(f"[DEBUG] Successfully imported scrape_profile")
        except ImportError as e:
            print(f"[ERROR] Cannot import scrape_profile: {e}")
            return 0
        
        # Scrape user profile
        url = f"https://www.threads.net/@{username}"
        print(f"[DEBUG] Scraping URL: {url}")
        
        data = scrape_profile(url)
        print(f"[DEBUG] Scrape result type: {type(data)}")
        print(f"[DEBUG] Scrape result: {json.dumps(data, indent=2) if data else 'None'}")
        
        if not data:
            print(f"[WARNING] No data returned for user: {username}")
            return 0
            
        # Handle different possible data structures
        posts = []
        if isinstance(data, dict):
            if 'posts' in data:
                posts = data['posts']
            elif 'data' in data and isinstance(data['data'], list):
                posts = data['data']
            elif isinstance(data, list):
                posts = data
        elif isinstance(data, list):
            posts = data
        
        print(f"[DEBUG] Found {len(posts)} posts for {username}")
        
        if not posts:
            print(f"[WARNING] No posts found for user: {username}")
            return 0
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        csv_file = "data/user_his.csv"
        
        # Create CSV with headers if it doesn't exist
        file_exists = os.path.exists(csv_file)
        if not file_exists:
            print(f"[DEBUG] Creating new CSV file: {csv_file}")
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['username', 'post_text', 'timestamp', 'url', 'crawl_date'])
        
        # Append posts to CSV file
        posts_saved = 0
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            for i, post in enumerate(posts):
                try:
                    print(f"[DEBUG] Processing post {i+1}/{len(posts)}: {post}")
                    
                    # Handle different post data structures
                    if isinstance(post, dict):
                        post_text = post.get('text', post.get('content', '')).strip()
                        timestamp = post.get('timestamp', post.get('date', post.get('time', '')))
                        post_url = post.get('url', post.get('link', ''))
                    elif isinstance(post, str):
                        post_text = post.strip()
                        timestamp = ''
                        post_url = ''
                    else:
                        print(f"[WARNING] Unknown post format: {type(post)}")
                        continue
                    
                    crawl_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Only save posts with actual content
                    if post_text and len(post_text.strip()) > 0:
                        writer.writerow([
                            username,
                            post_text,
                            timestamp,
                            post_url,
                            crawl_date
                        ])
                        posts_saved += 1
                        print(f"[DEBUG] Saved post {posts_saved}: {post_text[:50]}...")
                    else:
                        print(f"[WARNING] Empty post text, skipping")
                        
                except Exception as e:
                    print(f"[ERROR] Error processing post {i+1} for {username}: {e}")
                    continue
        
        print(f"[SUCCESS] Successfully saved {posts_saved} posts for {username}")
        return posts_saved
        
    except Exception as e:
        print(f"[ERROR] Error crawling user {username}: {e}")
        import traceback
        traceback.print_exc()
        return 0

def test_scrape_profile():
    """Test the scrape_profile function"""
    try:
        from thread.scrape_profile import scrape_profile
        
        # Test with a simple user
        test_username = "threads"  # Official Threads account
        test_url = f"https://www.threads.net/@{test_username}"
        
        print(f"[TEST] Testing scrape_profile with: {test_url}")
        result = scrape_profile(test_url)
        
        print(f"[TEST] Result type: {type(result)}")
        print(f"[TEST] Result: {json.dumps(result, indent=2) if result else 'None'}")
        
        return result
        
    except Exception as e:
        print(f"[TEST ERROR] Error testing scrape_profile: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python crawl_user_history.py <username>")
        print("       python crawl_user_history.py --test")
        sys.exit(1)
    
    if sys.argv[1] == '--test':
        print("Running test mode...")
        test_scrape_profile()
        return
    
    username = sys.argv[1].strip().replace('@', '')
    print(f"[MAIN] Starting crawl for username: {username}")
    
    posts_count = crawl_single_user_history(username)
    
    # Output for parent process to parse
    print(f"[RESULT] {posts_count} posts saved for {username}")
    
    return posts_count

if __name__ == "__main__":
    main()