import json
import csv
import os
import time
import sys
from scrape_profile import scrape_profile

def crawl_users_by_keyword(user_input=None):
    """
    Crawl user data by user_id input
    Returns: dict with status and data
    """
    try:
        # B1: Parse user input - can be single user or comma-separated list
        target_users = set()
        
        if user_input:
            # Split by comma and clean up usernames
            user_list = [u.strip().replace('@', '') for u in user_input.split(',')]
            target_users = set(filter(None, user_list))  # Remove empty strings
        
        if not target_users:
            return {
                "status": "warning",
                "message": "No user input provided. Please enter username(s) to crawl.",
                "data": {"total_users": 0, "users": []}
            }

        # B2: Store data for all users
        all_user_data = []
        successful_crawls = 0
        failed_crawls = 0

        # B3: Crawl each user
        for username in sorted(target_users):
            try:
                print(f"Crawling user: {username}")
                url = f"https://www.threads.net/@{username}"
                data = scrape_profile(url)

                if data:
                    all_user_data.append(data)
                    successful_crawls += 1
                    print(f"  -> Successfully crawled user: {username}")
                else:
                    failed_crawls += 1
                    print(f"  -> Failed to crawl user: {username} (no data returned)")

                time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"Error crawling {username}: {e}")
                failed_crawls += 1

        # B4: Save data to JSON file
        os.makedirs("data", exist_ok=True)
        output_file = "data/all_users_data.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_user_data, f, indent=2, ensure_ascii=False)

        return {
            "status": "success",
            "message": f"Successfully crawled {successful_crawls} users, {failed_crawls} failed",
            "data": {
                "total_users": len(all_user_data),
                "successful_crawls": successful_crawls,
                "failed_crawls": failed_crawls,
                "user_input": user_input,
                "usernames_crawled": list(target_users),
                "output_file": output_file,
                "users": all_user_data
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error during crawling: {str(e)}",
            "data": None
        }

def main():
    """Command line interface"""
    user_input = sys.argv[1] if len(sys.argv) > 1 else None
    if not user_input:
        print("Usage: python crawl_users_data.py <username1,username2,...>")
        print("Example: python crawl_users_data.py bao_hhani,mei.hwng_")
        return
    
    result = crawl_users_by_keyword(user_input)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result

if __name__ == "__main__":
    main()
