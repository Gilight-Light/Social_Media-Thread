from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import os
import pandas as pd
import json
import csv
import traceback
import subprocess

app = Flask(__name__)


# Store task status
task_status = {}

def load_existing_data():
    """Load existing data files for display"""
    data_info = {
        "main_post": {"exists": False, "count": 0, "last_modified": None, "symptom_groups": []},
        "users_data": {"exists": False, "count": 0, "last_modified": None}
    }
    
    # Check main_posts.csv
    if os.path.exists("data/main_posts.csv"):
        try:
            df = pd.read_csv("data/main_posts.csv")
            data_info["main_post"]["exists"] = True
            data_info["main_post"]["count"] = len(df)
            data_info["main_post"]["last_modified"] = datetime.fromtimestamp(
                os.path.getmtime("data/main_posts.csv")
            ).strftime("%Y-%m-%d %H:%M:%S")
            
            # Get unique symptom groups
            if 'symptom_group' in df.columns:
                data_info["main_post"]["symptom_groups"] = sorted(df['symptom_group'].dropna().unique().tolist())
            else:
                data_info["main_post"]["symptom_groups"] = []
                
        except Exception as e:
            print(f"Error loading main_posts.csv: {e}")
    
    # Check users history data from JSONL file
    if os.path.exists("data/all_users_history_data.jsonl"):
        try:
            user_count = 0
            with open("data/all_users_history_data.jsonl", 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            json.loads(line)
                            user_count += 1
                        except json.JSONDecodeError:
                            continue
            
            if user_count > 0:
                data_info["users_data"]["exists"] = True
                data_info["users_data"]["count"] = user_count
                data_info["users_data"]["last_modified"] = datetime.fromtimestamp(
                    os.path.getmtime("data/all_users_history_data.jsonl")
                ).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Error loading all_users_history_data.jsonl: {e}")
    
    return data_info

@app.route('/')
def index():
    """Main page"""
    data_info = load_existing_data()
    print(f"[DEBUG] Data info for template: {data_info}")
    return render_template('index.html', data_info=data_info)

@app.route('/debug_data')
def debug_data():
    """Debug endpoint to check data"""
    try:
        if not os.path.exists("data/main_posts.csv"):
            return jsonify({"error": "main_posts.csv not found"})
        
        df = pd.read_csv("data/main_posts.csv")
        
        symptom_groups = []
        if 'symptom_group' in df.columns:
            symptom_groups = sorted(df['symptom_group'].dropna().unique().tolist())
        
        return jsonify({
            "file_exists": True,
            "total_rows": len(df),
            "columns": list(df.columns),
            "symptom_groups": symptom_groups,
            "sample_data": df.head(3).to_dict('records')
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/filter_posts', methods=['POST'])
def filter_posts():
    """API endpoint to filter posts by symptom group"""
    try:
        print(f"[DEBUG] /filter_posts endpoint called")
        
        # Get JSON data
        data = request.get_json()
        if not data:
            print(f"[DEBUG] No JSON data received")
            return jsonify({
                "status": "error",
                "message": "No data received"
            })
        
        symptom_group = data.get('symptom_group', '').strip()
        print(f"[DEBUG] Received symptom_group: '{symptom_group}'")
        
        if not symptom_group:
            return jsonify({
                "status": "error",
                "message": "No symptom group provided"
            })
        
        # Check if file exists
        if not os.path.exists("data/main_posts.csv"):
            return jsonify({
                "status": "error",
                "message": "main_posts.csv not found"
            })
        
        # Read and filter data
        df = pd.read_csv("data/main_posts.csv")
        print(f"[DEBUG] Loaded {len(df)} rows from CSV")
        print(f"[DEBUG] Columns: {list(df.columns)}")
        
        if 'symptom_group' not in df.columns:
            return jsonify({
                "status": "error",
                "message": f"symptom_group column not found. Available columns: {list(df.columns)}"
            })
        
        # Show available symptom groups
        available_groups = df['symptom_group'].dropna().unique().tolist()
        print(f"[DEBUG] Available symptom groups: {available_groups}")
        
        # Filter data
        filtered_df = df[df['symptom_group'] == symptom_group]
        print(f"[DEBUG] Filtered to {len(filtered_df)} rows")
        
        if len(filtered_df) == 0:
            return jsonify({
                "status": "warning",
                "message": f"No posts found for '{symptom_group}'. Available: {available_groups}"
            })
        
        # Save filtered data
        os.makedirs("data", exist_ok=True)
        filtered_df.to_csv("data/filtered_posts.csv", index=False)
        
        # Convert to records for JSON
        posts_records = filtered_df.to_dict('records')
        print(f"[DEBUG] Returning {len(posts_records)} posts")
        
        return jsonify({
            "status": "success",
            "message": f"Found {len(filtered_df)} posts for '{symptom_group}'",
            "data": {
                "symptom_group": symptom_group,
                "posts_count": len(filtered_df),
                "output_file": "data/filtered_posts.csv",
                "posts": posts_records
            }
        })
        
    except Exception as e:
        print(f"[DEBUG] Exception in /filter_posts: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        })

@app.route('/view_main_post')
def view_main_post():
    """View main post data"""
    try:
        # Check for filtered posts first, then main posts
        if os.path.exists("data/filtered_posts.csv"):
            df = pd.read_csv("data/filtered_posts.csv")
            message = f"Showing {len(df)} filtered records"
            print(f"[DEBUG] Loading filtered posts: {len(df)} records")
        elif os.path.exists("data/main_posts.csv"):
            df = pd.read_csv("data/main_posts.csv")
            message = f"Showing all {len(df)} records"
            print(f"[DEBUG] Loading main posts: {len(df)} records")
        else:
            return jsonify({
                "status": "error",
                "message": "No main post data found"
            })
        
        # Convert to records for JSON response
        data = df.to_dict('records')
        
        # Add additional metadata
        response_data = {
            "status": "success",
            "message": message,
            "data": data,
            "total_count": len(data),
            "is_filtered": os.path.exists("data/filtered_posts.csv")
        }
        
        if os.path.exists("data/filtered_posts.csv") and 'symptom_group' in df.columns:
            unique_symptoms = df['symptom_group'].dropna().unique().tolist()
            if unique_symptoms:
                response_data["filtered_symptom"] = unique_symptoms[0]
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in view_main_post: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error reading main post: {str(e)}"
        })

@app.route('/clear_filter', methods=['POST'])
def clear_filter():
    """Clear the filtered posts file"""
    try:
        if os.path.exists("data/filtered_posts.csv"):
            os.remove("data/filtered_posts.csv")
            return jsonify({
                "status": "success",
                "message": "Filter cleared successfully"
            })
        else:
            return jsonify({
                "status": "info",
                "message": "No filter to clear"
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error clearing filter: {str(e)}"
        })

@app.route('/start_users_crawl', methods=['POST'])
def start_users_crawl():
    """Start crawling users from filtered posts - using existing data"""
    try:
        # Check if filtered posts exist
        if not os.path.exists("data/filtered_posts.csv"):
            return jsonify({
                "status": "error",
                "message": "No filtered posts found. Please filter posts first."
            })
        
        # Read filtered posts
        df = pd.read_csv("data/filtered_posts.csv")
        
        if df.empty:
            return jsonify({
                "status": "error", 
                "message": "Filtered posts file is empty"
            })
        
        # Get first 7 unique users
        unique_users = df['username'].dropna().unique()[:7]
        
        if len(unique_users) == 0:
            return jsonify({
                "status": "error",
                "message": "No valid usernames found in filtered posts"
            })
        
        print(f"[DEBUG] Looking for {len(unique_users)} users in existing data: {list(unique_users)}")
        
        # Use existing data instead of crawling
        result = get_users_from_existing_data(list(unique_users))
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in start_users_crawl: {e}")
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Error starting users crawl: {str(e)}"
        })

def get_users_from_existing_data(usernames):
    """Get user data from existing all_users_history_data.jsonl file"""
    try:
        print(f"[DEBUG] Getting users from existing data: {usernames}")
        
        # Check if the existing data file exists
        existing_data_file = "data/all_users_history_data.jsonl"
        if not os.path.exists(existing_data_file):
            return {
                "status": "error",
                "message": "No existing user data found (file doesn't exist). Please run the actual crawl first.",
                "data": None
            }
        
        # Check if file is empty
        if os.path.getsize(existing_data_file) == 0:
            return {
                "status": "error",
                "message": "Existing user data file is empty. Please run the actual crawl first.",
                "data": None
            }
        
        # Read existing JSONL data
        existing_users = {}
        found_users = []
        total_posts = 0
        line_count = 0
        
        try:
            with open(existing_data_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                        
                    try:
                        user_data = json.loads(line)
                        line_count += 1
                        
                        # Handle different possible data structures
                        username = None
                        if isinstance(user_data, dict):
                            username = user_data.get('username') or user_data.get('user_id') or user_data.get('name')
                        
                        if username:
                            existing_users[username] = user_data
                            print(f"[DEBUG] Loaded user: {username}")
                        else:
                            print(f"[DEBUG] Line {line_num}: No username found in data: {str(user_data)[:100]}...")
                            
                    except json.JSONDecodeError as e:
                        print(f"[DEBUG] JSON decode error on line {line_num}: {e}")
                        print(f"[DEBUG] Line content: {line[:100]}...")
                        continue
                        
        except Exception as e:
            print(f"[ERROR] Error reading JSONL file: {e}")
            return {
                "status": "error", 
                "message": f"Error reading existing data file: {str(e)}",
                "data": None
            }
        
        print(f"[DEBUG] Processed {line_count} lines, found {len(existing_users)} valid users")
        print(f"[DEBUG] Available users: {list(existing_users.keys())[:10]}...")  # Show first 10
        
        if len(existing_users) == 0:
            return {
                "status": "error",
                "message": "No valid user data found in existing file. The file may be corrupted or empty.",
                "data": None
            }
        
        # Filter for requested users
        for username in usernames:
            if username in existing_users:
                user_data = existing_users[username]
                found_users.append(user_data)
                
                # Count posts/threads - handle different data structures
                threads = []
                if isinstance(user_data, dict):
                    threads = user_data.get('threads', user_data.get('posts', user_data.get('data', [])))
                
                if isinstance(threads, list):
                    total_posts += len(threads)
                    print(f"[DEBUG] Found user {username} with {len(threads)} posts")
                else:
                    print(f"[DEBUG] Found user {username} but no valid posts data")
            else:
                print(f"[DEBUG] User {username} not found in existing data")
        
        if len(found_users) == 0:
            available_users = ", ".join(list(existing_users.keys())[:5])
            return {
                "status": "warning",
                "message": f"None of the requested users were found in existing data. Available users include: {available_users}...",
                "data": {
                    "total_users": len(usernames),
                    "successful_crawls": 0,
                    "failed_crawls": len(usernames),
                    "total_posts": 0,
                    "usernames": usernames,
                    "available_users": list(existing_users.keys())[:20]  # First 20 available users
                }
            }
        
        successful_crawls = len(found_users)
        failed_crawls = len(usernames) - successful_crawls
        
        # Save filtered user data to CSV for consistency
        csv_file = "data/user_his.csv"
        os.makedirs("data", exist_ok=True)
        
        posts_saved = 0
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'post_text', 'timestamp', 'url', 'crawl_date'])
            
            for user_data in found_users:
                username = user_data.get('username', user_data.get('user_id', ''))
                
                # Handle different thread data structures
                threads = user_data.get('threads', user_data.get('posts', user_data.get('data', [])))
                
                if isinstance(threads, list):
                    for thread in threads:
                        if isinstance(thread, dict):
                            post_text = thread.get('text', thread.get('content', '')).strip()
                            timestamp = thread.get('published_on', thread.get('timestamp', ''))
                            post_url = thread.get('url', thread.get('link', ''))
                        else:
                            post_text = str(thread).strip() if thread else ''
                            timestamp = ''
                            post_url = ''
                        
                        crawl_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        if post_text:
                            writer.writerow([
                                username,
                                post_text,
                                timestamp,
                                post_url,
                                crawl_date
                            ])
                            posts_saved += 1
        
        return {
            "status": "success",
            "message": f"Retrieved {successful_crawls} users from existing data, {failed_crawls} not found. {posts_saved} posts saved.",
            "data": {
                "total_users": len(usernames),
                "successful_crawls": successful_crawls,
                "failed_crawls": failed_crawls,
                "total_posts": posts_saved,
                "usernames": usernames,
                "found_usernames": [u.get('username', u.get('user_id', '')) for u in found_users],
                "output_file": csv_file,
                "source": "existing_data"
            }
        }
        
    except Exception as e:
        print(f"Error in get_users_from_existing_data: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Error retrieving users from existing data: {str(e)}",
            "data": None
        }

@app.route('/start_crawl', methods=['POST'])
def start_crawl():
    """Start the crawling process for new users"""
    try:
        # Get parameters from request
        data = request.get_json()
        if not data or 'symptom_group' not in data:
            return jsonify({
                "status": "error",
                "message": "Invalid data received"
            })
        
        symptom_group = data['symptom_group']
        print(f"[DEBUG] Starting crawl for symptom group: {symptom_group}")
        
        # Update task status
        task_id = "crawl_task_1"
        task_status[task_id] = {
            "status": "in_progress",
            "message": f"Crawling users for {symptom_group}",
            "progress": 0
        }
        
        # Simulate a long-running task (e.g., crawling)
        import time
        time.sleep(5)  # Replace with actual crawling logic
        
        # Update task status
        task_status[task_id]["status"] = "completed"
        task_status[task_id]["message"] = "Crawling completed"
        task_status[task_id]["progress"] = 100
        
        return jsonify({
            "status": "success",
            "message": "Crawling started",
            "task_id": task_id
        })
        
    except Exception as e:
        print(f"Error in start_crawl: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error starting crawl: {str(e)}"
        })

@app.route('/task_status/<task_id>')
def get_task_status(task_id):
    """Get the status of a specific task"""
    try:
        if task_id not in task_status:
            return jsonify({
                "status": "error",
                "message": "Invalid task ID"
            })
        
        status = task_status[task_id]
        
        return jsonify({
            "status": "success",
            "task_id": task_id,
            "task_status": status
        })
        
    except Exception as e:
        print(f"Error in get_task_status: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error retrieving task status: {str(e)}"
        })

@app.route('/download/<file_type>')
def download_file(file_type):
    """Download CSV files (main_posts or filtered_posts)"""
    try:
        if file_type == "main_posts":
            file_path = "data/main_posts.csv"
        elif file_type == "filtered_posts":
            file_path = "data/filtered_posts.csv"
        else:
            return jsonify({
                "status": "error",
                "message": "Invalid file type"
            })
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({
                "status": "error",
                "message": f"{file_type.replace('_', ' ').title()} not found"
            })
        
        # Send file for download
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        print(f"Error in download_file: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error downloading file: {str(e)}"
        })

@app.route('/export_users_data', methods=['POST'])
def export_users_data():
    """Export users data to CSV"""
    try:
        # Check if filtered posts exist
        if not os.path.exists("data/filtered_posts.csv"):
            return jsonify({
                "status": "error",
                "message": "No filtered posts found. Please filter posts first."
            })
        
        # Read filtered posts
        df = pd.read_csv("data/filtered_posts.csv")
        
        if df.empty:
            return jsonify({
                "status": "error", 
                "message": "Filtered posts file is empty"
            })
        
        # Get unique usernames
        unique_users = df['username'].dropna().unique()
        
        if len(unique_users) == 0:
            return jsonify({
                "status": "error",
                "message": "No valid usernames found in filtered posts"
            })
        
        print(f"[DEBUG] Found {len(unique_users)} unique users: {list(unique_users)}")
        
        # Prepare CSV export
        export_data = []
        for username in unique_users:
            user_posts = df[df['username'] == username]
            for _, post in user_posts.iterrows():
                export_data.append({
                    "username": username,
                    "post_content": post.get('post_content', ''),
                    "symptom_group": post.get('symptom_group', '')
                })
        
        # Create export DataFrame
        export_df = pd.DataFrame(export_data)
        
        # Save to CSV
        export_file = "data/users_export.csv"
        export_df.to_csv(export_file, index=False)
        
        return jsonify({
            "status": "success",
            "message": f"Exported {len(export_data)} records to {export_file}",
            "data": export_file
        })
        
    except Exception as e:
        print(f"Error in export_users_data: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error exporting users data: {str(e)}"
        })

@app.route('/run_analysis', methods=['POST'])
def run_analysis():
    """Run analysis on filtered posts"""
    try:
        # Check if filtered posts exist
        if not os.path.exists("data/filtered_posts.csv"):
            return jsonify({
                "status": "error",
                "message": "No filtered posts found. Please filter posts first."
            })
        
        # Read filtered posts
        df = pd.read_csv("data/filtered_posts.csv")
        
        if df.empty:
            return jsonify({
                "status": "error", 
                "message": "Filtered posts file is empty"
            })
        
        # Perform analysis - example: count posts per symptom group
        analysis_result = df.groupby('symptom_group').size().reset_index(name='counts')
        
        # Convert to records for JSON
        analysis_records = analysis_result.to_dict('records')
        
        return jsonify({
            "status": "success",
            "message": "Analysis completed",
            "data": analysis_records
        })
        
    except Exception as e:
        print(f"Error in run_analysis: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error running analysis: {str(e)}"
        })

@app.route('/visualize_data')
def visualize_data():
    """Visualize data - example route"""
    try:
        # Check if filtered posts exist
        if not os.path.exists("data/filtered_posts.csv"):
            return jsonify({
                "status": "error",
                "message": "No filtered posts found. Please filter posts first."
            })
        
        # Read filtered posts
        df = pd.read_csv("data/filtered_posts.csv")
        
        if df.empty:
            return jsonify({
                "status": "error", 
                "message": "Filtered posts file is empty"
            })
        
        # Example visualization - count posts per symptom group
        visualization_data = df.groupby('symptom_group').size().reset_index(name='counts')
        
        # Convert to records for JSON
        viz_records = visualization_data.to_dict('records')
        
        return jsonify({
            "status": "success",
            "message": "Visualization data prepared",
            "data": viz_records
        })
        
    except Exception as e:
        print(f"Error in visualize_data: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error preparing visualization data: {str(e)}"
        })

@app.route('/settings')
def settings():
    """User settings page"""
    return render_template('settings.html')

@app.route('/update_settings', methods=['POST'])
def update_settings():
    """Update user settings"""
    try:
        # Get settings data
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data received"
            })
        
        # For now, just echo back the settings
        return jsonify({
            "status": "success",
            "message": "Settings updated",
            "data": data
        })
        
    except Exception as e:
        print(f"Error in update_settings: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error updating settings: {str(e)}"
        })

@app.route('/help')
def help_page():
    """Help and documentation page"""
    return render_template('help.html')

@app.route('/api/data_summary')
def api_data_summary():
    """API endpoint to get a summary of the data"""
    try:
        # Check if main posts exist
        if not os.path.exists("data/main_posts.csv"):
            return jsonify({
                "status": "error",
                "message": "No main posts data found"
            })
        
        # Read main posts
        df = pd.read_csv("data/main_posts.csv")
        
        if df.empty:
            return jsonify({
                "status": "error", 
                "message": "Main posts file is empty"
            })
        
        # Summary statistics
        total_posts = len(df)
        symptom_groups = df['symptom_group'].dropna().unique().tolist()
        
        return jsonify({
            "status": "success",
            "data": {
                "total_posts": total_posts,
                "symptom_groups": symptom_groups
            }
        })
        
    except Exception as e:
        print(f"Error in api_data_summary: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error retrieving data summary: {str(e)}"
        })

@app.route('/api/symptom_groups')
def api_symptom_groups():
    """API endpoint to get all symptom groups"""
    try:
        # Check if main posts exist
        if not os.path.exists("data/main_posts.csv"):
            return jsonify({
                "status": "error",
                "message": "No main posts data found"
            })
        
        # Read main posts
        df = pd.read_csv("data/main_posts.csv")
        
        if df.empty:
            return jsonify({
                "status": "error", 
                "message": "Main posts file is empty"
            })
        
        # Get unique symptom groups
        symptom_groups = df['symptom_group'].dropna().unique().tolist()
        
        return jsonify({
            "status": "success",
            "data": symptom_groups
        })
        
    except Exception as e:
        print(f"Error in api_symptom_groups: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error retrieving symptom groups: {str(e)}"
        })

@app.route('/api/post_content', methods=['POST'])
def api_post_content():
    """API endpoint to get post content by ID"""
    try:
        # Get post ID from request
        data = request.get_json()
        post_id = data.get('id')
        
        if not post_id:
            return jsonify({
                "status": "error",
                "message": "No post ID provided"
            })
        
        # Check if main posts exist
        if not os.path.exists("data/main_posts.csv"):
            return jsonify({
                "status": "error",
                "message": "No main posts data found"
            })
        
        # Read main posts
        df = pd.read_csv("data/main_posts.csv")
        
        if df.empty:
            return jsonify({
                "status": "error", 
                "message": "Main posts file is empty"
            })
        
        # Get post content by ID
        post = df[df['id'] == post_id]
        
        if len(post) == 0:
            return jsonify({
                "status": "error",
                "message": "Post not found"
            })
        elif len(post) > 1:
            return jsonify({
                "status": "error",
                "message": "Multiple posts found with the same ID"
            })
        
        # Convert post data to dictionary
        post_data = post.iloc[0].to_dict()
        
        return jsonify({
            "status": "success",
            "data": post_data
        })
        
    except Exception as e:
        print(f"Error in api_post_content: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error retrieving post content: {str(e)}"
        })

@app.route('/api/save_post', methods=['POST'])
def api_save_post():
    """API endpoint to save a new post"""
    try:
        # Get post data from request
        data = request.get_json()
        
        if not data or 'content' not in data or 'symptom_group' not in data:
            return jsonify({
                "status": "error",
                "message": "Invalid post data"
            })
        
        # Create new post ID
        new_id = None
        if os.path.exists("data/main_posts.csv"):
            df = pd.read_csv("data/main_posts.csv")
            if not df.empty:
                new_id = df['id'].max() + 1
        
        # If no existing posts, start ID from 1
        if new_id is None:
            new_id = 1
        
        # Prepare new post record
        new_post = {
            "id": new_id,
            "content": data['content'],
            "symptom_group": data['symptom_group'],
            "username": data.get('username', ''),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Append to CSV
        file_exists = os.path.exists("data/main_posts.csv")
        with open("data/main_posts.csv", mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=new_post.keys())
            # Write header only if file is new
            if not file_exists:
                writer.writeheader()
            writer.writerow(new_post)
        
        return jsonify({
            "status": "success",
            "message": "Post saved successfully",
            "data": new_post
        })
        
    except Exception as e:
        print(f"Error in api_save_post: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error saving post: {str(e)}"
        })

@app.route('/api/delete_post', methods=['POST'])
def api_delete_post():
    """API endpoint to delete a post"""
    try:
        # Get post ID from request
        data = request.get_json()
        post_id = data.get('id')
        
        if not post_id:
            return jsonify({
                "status": "error",
                "message": "No post ID provided"
            })
        
        # Read existing posts
        df = pd.read_csv("data/main_posts.csv")
        
        # Check if post exists
        if post_id not in df['id'].values:
            return jsonify({
                "status": "error",
                "message": "Post not found"
            })
        
        # Delete post
        df = df[df['id'] != post_id]
        
        # Save updated posts back to CSV
        df.to_csv("data/main_posts.csv", index=False)
        
        return jsonify({
            "status": "success",
            "message": "Post deleted successfully"
        })
        
    except Exception as e:
        print(f"Error in api_delete_post: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error deleting post: {str(e)}"
        })

@app.route('/api/update_post', methods=['POST'])
def api_update_post():
    """API endpoint to update a post"""
    try:
        # Get post data from request
        data = request.get_json()
        
        if not data or 'id' not in data or 'content' not in data:
            return jsonify({
                "status": "error",
                "message": "Invalid post data"
            })
        
        post_id = data['id']
        
        # Read existing posts
        df = pd.read_csv("data/main_posts.csv")
        
        # Check if post exists
        if post_id not in df['id'].values:
            return jsonify({
                "status": "error",
                "message": "Post not found"
            })
        
        # Update post content
        df.loc[df['id'] == post_id, 'content'] = data['content']
        df.loc[df['id'] == post_id, 'symptom_group'] = data.get('symptom_group', df.loc[df['id'] == post_id, 'symptom_group'])
        
        # Save updated posts back to CSV
        df.to_csv("data/main_posts.csv", index=False)
        
        return jsonify({
            "status": "success",
            "message": "Post updated successfully"
        })
        
    except Exception as e:
        print(f"Error in api_update_post: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error updating post: {str(e)}"
        })

@app.route('/api/crawl_status')
def api_crawl_status():
    """API endpoint to get the status of the crawl"""
    try:
        # For now, just return the task status
        return jsonify({
            "status": "success",
            "data": task_status
        })
        
    except Exception as e:
        print(f"Error in api_crawl_status: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error retrieving crawl status: {str(e)}"
        })

@app.route('/api/system_info')
def api_system_info():
    """API endpoint to get system information"""
    try:
        # Get basic system info
        python_version = sys.version
        flask_version = Flask.__version__
        
        return jsonify({
            "status": "success",
            "data": {
                "python_version": python_version,
                "flask_version": flask_version,
                "task_status": task_status
            }
        })
        
    except Exception as e:
        print(f"Error in api_system_info: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error retrieving system info: {str(e)}"
        })

def run_crawl_task(symptom_group):
    """Run the crawl task - to be executed in a separate thread"""
    try:
        print(f"[DEBUG] Starting crawl task for {symptom_group}")
        
        # Simulate crawling - replace with actual crawling logic
        import time
        time.sleep(10)
        
        print(f"[DEBUG] Crawl task completed for {symptom_group}")
        
        # Update task status
        task_status["crawl_task_1"]["status"] = "completed"
        task_status["crawl_task_1"]["message"] = "Crawling completed"
        task_status["crawl_task_1"]["progress"] = 100
        
    except Exception as e:
        print(f"Error in run_crawl_task: {e}")
        task_status["crawl_task_1"]["status"] = "error"
        task_status["crawl_task_1"]["message"] = f"Error: {str(e)}"

@app.route('/view_user_history')
def view_user_history():
    """View user history data from CSV file"""
    try:
        csv_file = "data/user_his.csv"
        
        if not os.path.exists(csv_file):
            return jsonify({
                "status": "error",
                "message": "No user history data found. Please crawl users first."
            })
        
        # Read CSV data
        df = pd.read_csv(csv_file)
        
        if df.empty:
            return jsonify({
                "status": "warning", 
                "message": "User history file is empty."
            })
        
        # Convert to records for JSON response
        data = df.to_dict('records')
        
        return jsonify({
            "status": "success",
            "message": f"Found {len(data)} user history records",
            "data": data,
            "total_count": len(data),
            "file_path": csv_file
        })
        
    except Exception as e:
        print(f"Error in view_user_history: {e}")
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Error reading user history: {str(e)}"
        })

@app.route('/download_user_history')
def download_user_history():
    """Download user history CSV file"""
    try:
        csv_file = "data/user_his.csv"
        
        if not os.path.exists(csv_file):
            return jsonify({
                "status": "error",
                "message": "No user history data found to download."
            })
        
        return send_file(csv_file, as_attachment=True, download_name="user_history.csv")
        
    except Exception as e:
        print(f"Error in download_user_history: {e}")
        return jsonify({
            "status": "error", 
            "message": f"Error downloading user history: {str(e)}"
        })

@app.route('/view_users_data')
def view_users_data():
    """View users data from JSONL file"""
    try:
        jsonl_file = "data/all_users_history_data.jsonl"
        
        if not os.path.exists(jsonl_file):
            return jsonify({
                "status": "error",
                "message": "No users data found. User history file doesn't exist."
            })
        
        # Read JSONL data and convert to flattened format for table display
        users_data = []
        total_posts = 0
        
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    user_data = json.loads(line)
                    username = user_data.get('username', f'User_{line_num}')
                    threads = user_data.get('threads', [])
                    
                    # Create summary record for each user
                    user_summary = {
                        'username': username,
                        'total_posts': len(threads),
                        'latest_post': '',
                        'oldest_post': '',
                        'sample_post': ''
                    }
                    
                    if threads:
                        # Get latest and oldest posts based on timestamp if available
                        posts_with_time = []
                        for thread in threads:
                            if isinstance(thread, dict):
                                timestamp = thread.get('timestamp', 0)
                                text = thread.get('text', '').strip()
                                if text:
                                    posts_with_time.append({
                                        'timestamp': timestamp,
                                        'text': text[:100] + '...' if len(text) > 100 else text,
                                        'published_on': thread.get('published_on', '')
                                    })
                        
                        if posts_with_time:
                            # Sort by timestamp if available
                            if any(p['timestamp'] for p in posts_with_time):
                                posts_with_time.sort(key=lambda x: x['timestamp'], reverse=True)
                                user_summary['latest_post'] = posts_with_time[0]['text']
                                user_summary['oldest_post'] = posts_with_time[-1]['text']
                            else:
                                user_summary['latest_post'] = posts_with_time[0]['text']
                                user_summary['oldest_post'] = posts_with_time[-1]['text']
                            
                            user_summary['sample_post'] = posts_with_time[0]['text']
                    
                    users_data.append(user_summary)
                    total_posts += len(threads)
                    
                except json.JSONDecodeError as e:
                    print(f"JSON decode error on line {line_num}: {e}")
                    continue
        
        if not users_data:
            return jsonify({
                "status": "warning",
                "message": "No valid user data found in the file."
            })
        
        return jsonify({
            "status": "success",
            "message": f"Found {len(users_data)} users with {total_posts} total posts",
            "data": users_data,
            "total_count": len(users_data),
            "total_posts": total_posts,
            "data_type": "users_summary"
        })
        
    except Exception as e:
        print(f"Error in view_users_data: {e}")
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Error reading users data: {str(e)}"
        })

if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(debug=True, port=5000)
