from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import json
import os
import pandas as pd
from datetime import datetime
import threading
import time
import asyncio
from crawl_users_data import crawl_users_by_keyword
from crawl_main_posts import crawl_main_posts_from_lexicon  # Updated import

app = Flask(__name__)

# Store task status
task_status = {}

def run_topic_crawl_async(task_id, topic):
    """Run the topic-based post crawler asynchronously"""
    try:
        task_status[task_id] = {
            "status": "running", 
            "message": f"Crawling posts for topic: {topic}..."
        }
        
        print(f"[DEBUG] Starting topic crawl for: '{topic}'")
        
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the async function
            loop.run_until_complete(crawl_main_posts_from_lexicon(topic))
            
            # Check if file was created successfully
            if os.path.exists("data/main_posts.csv"):
                df = pd.read_csv("data/main_posts.csv")
                posts_count = len(df)
                
                result = {
                    "status": "success",
                    "message": f"Successfully crawled {posts_count} posts for topic: {topic}",
                    "data": {
                        "topic": topic,
                        "posts_count": posts_count,
                        "output_file": "data/main_posts.csv"
                    }
                }
            else:
                result = {
                    "status": "error",
                    "message": "Crawling completed but no output file was created",
                    "topic_input": topic
                }
        finally:
            loop.close()
        
        print(f"[DEBUG] Topic crawl result: {result}")
        
        # Update task status with the result
        task_status[task_id] = result
        
    except Exception as e:
        error_msg = f"Exception occurred: {str(e)}"
        print(f"[DEBUG] Exception in topic crawl: {error_msg}")
        task_status[task_id] = {
            "status": "error",
            "message": error_msg,
            "topic_input": topic
        }

def run_users_crawl_async(task_id, user_parameter):
    """Run the users crawler asynchronously with parameter"""
    try:
        task_status[task_id] = {
            "status": "running", 
            "message": f"Crawling users with parameter: {user_parameter}..."
        }
        
        print(f"[DEBUG] Starting users crawl with parameter: '{user_parameter}'")
        
        # Use the function interface directly
        result = crawl_users_by_keyword(user_parameter if user_parameter else None)
        
        print(f"[DEBUG] Users crawl result: {result}")
        
        # Add the input parameter to the result for verification
        result["user_parameter"] = user_parameter
        task_status[task_id] = result
        
    except Exception as e:
        error_msg = f"Exception occurred: {str(e)}"
        print(f"[DEBUG] Exception in users crawl: {error_msg}")
        task_status[task_id] = {
            "status": "error",
            "message": error_msg,
            "user_parameter": user_parameter
        }

def load_existing_data():
    """Load existing data files for display"""
    data_info = {
        "main_post": {"exists": False, "count": 0, "last_modified": None},
        "users_data": {"exists": False, "count": 0, "last_modified": None}
    }
    
    # Check main_posts.csv (note: changed to main_posts.csv to match your crawler output)
    if os.path.exists("data/main_posts.csv"):
        try:
            df = pd.read_csv("data/main_posts.csv")
            data_info["main_post"]["exists"] = True
            data_info["main_post"]["count"] = len(df)
            data_info["main_post"]["last_modified"] = datetime.fromtimestamp(
                os.path.getmtime("data/main_posts.csv")
            ).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Error loading main_posts.csv: {e}")
    
    # Check users data
    if os.path.exists("data/all_users_data.json"):
        try:
            with open("data/all_users_data.json", "r", encoding="utf-8") as f:
                users_data = json.load(f)
            data_info["users_data"]["exists"] = True
            data_info["users_data"]["count"] = len(users_data)
            data_info["users_data"]["last_modified"] = datetime.fromtimestamp(
                os.path.getmtime("data/all_users_data.json")
            ).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Error loading all_users_data.json: {e}")
    
    return data_info

@app.route('/')
def index():
    """Main page"""
    data_info = load_existing_data()
    return render_template('index.html', data_info=data_info)

@app.route('/crawl_topic', methods=['POST'])
def crawl_topic():
    """API endpoint to start topic-based post crawler"""
    try:
        data = request.get_json() or {}
        topic = data.get('topic', '').strip()
        
        print(f"[DEBUG] Received POST to /crawl_topic with data: {data}")
        print(f"[DEBUG] Extracted topic: '{topic}'")
        
        if not topic:
            return jsonify({
                "status": "error",
                "message": "No topic provided. Please enter a topic to search for."
            })
        
        task_id = f"topic_{int(time.time())}"
        
        # Start the task in a separate thread
        thread = threading.Thread(target=run_topic_crawl_async, args=(task_id, topic))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "started",
            "task_id": task_id,
            "message": f"Topic crawler started for: {topic}",
            "topic_input": topic
        })
    except Exception as e:
        error_msg = f"Server error: {str(e)}"
        print(f"[DEBUG] Exception in /crawl_topic: {error_msg}")
        return jsonify({
            "status": "error",
            "message": error_msg
        })

@app.route('/crawl_users', methods=['POST'])
def crawl_users():
    """API endpoint to start users crawler with parameter"""
    try:
        data = request.get_json() or {}
        user_parameter = data.get('user_parameter', '').strip()
        
        print(f"[DEBUG] Received POST to /crawl_users with data: {data}")
        print(f"[DEBUG] Extracted user_parameter: '{user_parameter}'")
        
        task_id = f"users_{int(time.time())}"
        
        # Start the task in a separate thread
        thread = threading.Thread(target=run_users_crawl_async, args=(task_id, user_parameter))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "started",
            "task_id": task_id,
            "message": f"Users crawler started with parameter: {user_parameter or 'None'}",
            "user_parameter": user_parameter
        })
    except Exception as e:
        error_msg = f"Server error: {str(e)}"
        print(f"[DEBUG] Exception in /crawl_users: {error_msg}")
        return jsonify({
            "status": "error",
            "message": error_msg
        })

@app.route('/task_status/<task_id>')
def get_task_status(task_id):
    """Get the status of a running task"""
    try:
        if task_id in task_status:
            return jsonify(task_status[task_id])
        else:
            return jsonify({
                "status": "not_found",
                "message": "Task not found"
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error getting task status: {str(e)}"
        })

@app.route('/view_main_post')
def view_main_post():
    """View main post data"""
    try:
        # Check for main_posts.csv (output from crawler)
        if os.path.exists("data/main_posts.csv"):
            df = pd.read_csv("data/main_posts.csv")
        elif os.path.exists("data/main_post.csv"):
            df = pd.read_csv("data/main_post.csv")
        else:
            return jsonify({
                "status": "error",
                "message": "No main post data found"
            })
        
        data = df.to_dict('records')
        
        return jsonify({
            "status": "success",
            "message": f"Loaded {len(data)} records",
            "data": data
        })
        
    except Exception as e:
        print(f"Error in view_main_post: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error reading main post: {str(e)}"
        })

@app.route('/view_users_data')
def view_users_data():
    """View users data with all threads/comments"""
    try:
        if not os.path.exists("data/all_users_data.json"):
            return jsonify({
                "status": "error",
                "message": "all_users_data.json not found"
            })
        
        with open("data/all_users_data.json", "r", encoding="utf-8") as f:
            users_data = json.load(f)
        
        # Transform data to show all threads/comments in a flat structure
        all_threads = []
        for user_item in users_data:
            user = user_item.get("user", {})
            threads = user_item.get("threads", [])
            
            for thread in threads:
                thread_record = {
                    "username": user.get("username", "N/A"),
                    "full_name": user.get("full_name", "N/A"),
                    "followers": user.get("followers", 0),
                    "is_verified": "Yes" if user.get("is_verified", False) else "No",
                    "thread_text": thread.get("text", ""),
                    "published_on": thread.get("published_on", ""),
                    "like_count": thread.get("like_count", 0),
                    "reply_count": thread.get("reply_count", 0),
                    "thread_url": thread.get("url", ""),
                    "thread_id": thread.get("id", "")
                }
                all_threads.append(thread_record)
        
        return jsonify({
            "status": "success",
            "message": f"Loaded {len(all_threads)} threads from {len(users_data)} users",
            "data": all_threads,
            "data_type": "threads"
        })
        
    except Exception as e:
        print(f"Error in view_users_data: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error reading users data: {str(e)}"
        })

@app.route('/get_data_info')
def get_data_info():
    """Get current data file information"""
    try:
        return jsonify(load_existing_data())
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error loading data info: {str(e)}"
        })

@app.route('/download/<file_type>')
def download_file(file_type):
    """Download data files"""
    try:
        if file_type == "main_post":
            if os.path.exists("data/main_posts.csv"):
                return send_file("data/main_posts.csv", as_attachment=True)
            elif os.path.exists("data/main_post.csv"):
                return send_file("data/main_post.csv", as_attachment=True)
        elif file_type == "users_data":
            if os.path.exists("data/all_users_data.json"):
                return send_file("data/all_users_data.json", as_attachment=True)
        
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    os.makedirs("data", exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)