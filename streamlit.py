import streamlit as st
import pandas as pd
import requests
import json
import time
from datetime import datetime
import numpy as np
import hashlib

# Cấu hình trang
st.set_page_config(
    page_title="Social Media Suicide Risk Analysis",
    page_icon="🧠",
    layout="wide"
)

# CSS tùy chỉnh - Modern & Professional with dual columns
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .risk-column {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
        min-height: 400px;
    }
    
    .high-risk-column {
        border-left: 5px solid #e74c3c;
    }
    
    .low-risk-column {
        border-left: 5px solid #27ae60;
    }
    
    .user-card {
        background: linear-gradient(145deg, #ffffff, #f8f9ff);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border: 1px solid #e3e8ff;
        animation: slideInFromLeft 0.5s ease-out;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .user-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }
    
    .high-risk-card {
        border-left: 4px solid #e74c3c;
        background: linear-gradient(145deg, #fff5f5, #fff);
    }
    
    .low-risk-card {
        border-left: 4px solid #27ae60;
        background: linear-gradient(145deg, #f5fff5, #fff);
    }
    
    @keyframes slideInFromLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .user-avatar {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
        margin-right: 1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .high-risk-avatar {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
    }
    
    .low-risk-avatar {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
    }
    
    .risk-badge-high {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        display: inline-flex;
        align-items: center;
        box-shadow: 0 3px 10px rgba(231, 76, 60, 0.3);
        animation: pulse 2s infinite;
    }
    
    .risk-badge-low {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        display: inline-flex;
        align-items: center;
        box-shadow: 0 3px 10px rgba(39, 174, 96, 0.3);
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .streaming-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        color: #667eea;
        font-weight: 600;
        margin: 1rem 0;
    }
    
    .loading-dots {
        display: inline-flex;
        margin-left: 10px;
    }
    
    .loading-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #667eea;
        margin: 0 2px;
        animation: loadingDots 1.4s ease-in-out infinite both;
    }
    
    .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
    .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes loadingDots {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        display: block;
    }
    
    .stat-label {
        color: #7f8c8d;
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .post-container {
        background: #f8f9ff;
        border: 1px solid #e8e8e8;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
    }
    
    .post-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .post-number {
        background: #667eea;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .post-timestamp {
        color: #7f8c8d;
        font-size: 0.9rem;
    }
    
    .post-content {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #2c3e50;
        margin: 1rem 0;
    }
    
    .column-header {
        text-align: center;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 10px;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .high-risk-header {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
    }
    
    .low-risk-header {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        color: white;
    }
    
    .masked-username {
        font-family: monospace;
        background: #f0f0f0;
        padding: 2px 6px;
        border-radius: 4px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🧠 REAL-TIME DETECTION OF DEPRESSION EXPRESSION ON THREADS POSTS</h1>
</div>
""", unsafe_allow_html=True)

# Utility function to mask usernames for privacy
def mask_username(username):
    """Mask username for privacy protection using consistent hashing"""
    if not username or len(username) < 3:
        return "User_***"
    
    # Create a consistent hash-based mask
    hash_value = hashlib.md5(username.encode()).hexdigest()[:6]
    return f"User_{hash_value}"

# Hàm tải dữ liệu
@st.cache_data(ttl=30)  # Reduced cache time for live updates
def load_data():
    try:
        response = requests.get("http://localhost:5000/view_user_history", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return data['data']
            else:
                st.error(f"API Error: {data['message']}")
                return []
        else:
            st.error(f"HTTP Error: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return []

def display_user_card(user_data, container):
    """Display user information card"""
    # Get original username and create masked version for display
    original_username = user_data.get('username', 'Unknown')
    masked_username = mask_username(original_username)
    
    suicide_risk = user_data.get('suicide_risk', 0)
    risk_score = user_data.get('risk_score', 0)
    stats = user_data.get('stats', {})
    main_posts = user_data.get('main_posts', [])
    detailed_posts = user_data.get('detailed_posts', [])
    
    # Risk styling
    if suicide_risk == 1:
        risk_color = "#ff4757"
        risk_label = "HIGH RISK"
        risk_icon = "⚠️"
        card_border = "border: 2px solid #ff4757;"
    else:
        risk_color = "#2ed573"
        risk_label = "LOW RISK"
        risk_icon = "✅"
        card_border = "border: 2px solid #2ed573;"
    
    # Create expandable user section using MASKED USERNAME
    with container.expander(f"{risk_icon} {masked_username} - {risk_label}", expanded=False):
        # User info header with MASKED USERNAME
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {risk_color}20, {risk_color}10); 
                   padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; {card_border}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="color: {risk_color}; margin: 0;">{masked_username}</h3>
                    <p style="margin: 0.5rem 0; color: #666;">
                        📊 Risk Score: <strong>{risk_score:.2f}</strong> | 
                        📝 Main Posts: <strong>{stats.get('total_main_posts', 0)}</strong> | 
                        🔍 Detailed Posts: <strong>{stats.get('total_detailed_posts', 0)}</strong>
                    </p>
                </div>
                <div style="text-align: center;">
                    <div style="background: {risk_color}; color: white; padding: 0.5rem 1rem; 
                               border-radius: 20px; font-weight: bold; font-size: 0.9rem;">
                        {risk_label}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Main Posts Section (Always visible - from main_posts.csv)
        if main_posts:
            st.markdown("### 📝 Main Posts (from main_posts.csv)")
            for i, post in enumerate(main_posts):
                # Mask username in post display as well
                display_username = mask_username(post.get('username', original_username))
                
                label = post.get('label', 0)
                label_color = "#ff4757" if label == 1 else "#2ed573"
                label_text = "HIGH RISK" if label == 1 else "LOW RISK"
                
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; 
                           margin: 0.5rem 0; border-left: 4px solid {label_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <strong style="color: #333;">@{display_username}</strong>
                        <span style="background: {label_color}; color: white; padding: 0.2rem 0.5rem; 
                                   border-radius: 10px; font-size: 0.8rem;">{label_text}</span>
                    </div>
                    <p style="margin: 0.5rem 0; color: #555;">{post.get('text', 'N/A')}</p>
                    <small style="color: #888;">
                        🕒 {post.get('timestamp', 'N/A')} | 
                        🏷️ {post.get('symptom_group', 'N/A')} | 
                        🔗 <a href="{post.get('url', '#')}" target="_blank">View Post</a>
                    </small>
                </div>
                """, unsafe_allow_html=True)
        
        # View Details Button
        if detailed_posts:
            if st.button(f"👁️ View Details ({len(detailed_posts)} posts)", 
                        key=f"details_{original_username}", 
                        help="Show detailed posts from user history"):
                
                st.markdown("### 🔍 Detailed Posts (from all_users_history_data.jsonl)")
                
                # Display detailed posts in a container
                with st.container():
                    for i, detail_post in enumerate(detailed_posts):
                        st.markdown(f"""
                        <div style="background: #fff3cd; padding: 1rem; border-radius: 10px; 
                                   margin: 0.5rem 0; border-left: 4px solid #ffc107;">
                            <div style="margin-bottom: 0.5rem;">
                                <strong style="color: #333;">@{masked_username}</strong>
                            </div>
                            <p style="margin: 0.5rem 0; color: #555;">{detail_post.get('post_text', 'N/A')}</p>
                            <small style="color: #888;">
                                🕒 {detail_post.get('timestamp', 'N/A')} | 
                                🔗 <a href="{detail_post.get('url', '#')}" target="_blank">View Post</a>
                            </small>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("📝 No detailed posts available for this user")

# Load data
user_data_list = load_data()

if user_data_list and len(user_data_list) > 0:
    # Khởi tạo session state
    if 'loaded_users' not in st.session_state:
        st.session_state.loaded_users = []
        st.session_state.streaming_started = False
        st.session_state.streaming_completed = False
        st.session_state.current_loading_index = 0
        st.session_state.all_users = user_data_list
        st.session_state.show_user_details = {}
        st.session_state.high_risk_users = []
        st.session_state.low_risk_users = []
    
    users = st.session_state.all_users
    
    # Control Panel
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 🎯 Real-time Analysis Control")
    
    with col2:
        if st.button("🚀 Bắt đầu Stream", type="primary", disabled=st.session_state.streaming_started):
            st.session_state.streaming_started = True
            st.session_state.loaded_users = []
            st.session_state.current_loading_index = 0
            st.session_state.streaming_completed = False
            st.session_state.show_user_details = {}
            st.session_state.high_risk_users = []
            st.session_state.low_risk_users = []
            st.rerun()
    
    with col3:
        if st.button("🔄 Reset Stream", type="secondary"):
            st.session_state.loaded_users = []
            st.session_state.streaming_started = False
            st.session_state.streaming_completed = False
            st.session_state.current_loading_index = 0
            st.session_state.show_user_details = {}
            st.session_state.high_risk_users = []
            st.session_state.low_risk_users = []
            st.rerun()
    
    # Statistics Overview
    total_users = len(users)
    high_risk_count = len([u for u in st.session_state.loaded_users if u.get('suicide_risk') == 1])
    low_risk_count = len([u for u in st.session_state.loaded_users if u.get('suicide_risk') == 0])
    total_main_posts = sum([len(u.get('main_posts', [])) for u in users])
    
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-card">
            <span class="stat-number">{total_users}</span>
            <div class="stat-label">Tổng số người dùng</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">{len(st.session_state.loaded_users)}</span>
            <div class="stat-label">Đã phân tích</div>
        </div>
        <div class="stat-card">
            <span class="stat-number" style="color: #e74c3c;">{high_risk_count}</span>
            <div class="stat-label">Nguy cơ cao</div>
        </div>
        <div class="stat-card">
            <span class="stat-number" style="color: #27ae60;">{low_risk_count}</span>
            <div class="stat-label">Nguy cơ thấp</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress Bar
    if len(users) > 0:
        progress = len(st.session_state.loaded_users) / len(users)
        st.progress(progress, text=f"Streaming: {len(st.session_state.loaded_users)}/{len(users)} người dùng ({progress*100:.1f}%)")
    
    # Main Streaming Area with Dual Columns
    st.markdown("## 📊 Live User Analysis Stream")
    
    # Create two columns for high risk and low risk users
    col_high, col_low = st.columns(2)
    
    with col_high:
        st.markdown("""
        <div class="column-header high-risk-header">
            🚨 Phát Hiện Biểu Hiện Trầm Cảm
        </div>
        """, unsafe_allow_html=True)
        
        high_risk_container = st.container()
        
        with high_risk_container:
            if st.session_state.high_risk_users:
                for user_data in st.session_state.high_risk_users:
                    display_user_card(user_data, col_high)

    
    with col_low:
        st.markdown("""
        <div class="column-header low-risk-header">
            ✅ Không Phát Hiện Biểu Hiện Trầm Cảm
        </div>
        """, unsafe_allow_html=True)
        
        low_risk_container = st.container()
        
        with low_risk_container:
            if st.session_state.low_risk_users:
                for user_data in st.session_state.low_risk_users:
                    display_user_card(user_data, col_low)

    
    # Streaming logic
    if st.session_state.streaming_started and not st.session_state.streaming_completed:
        if st.session_state.current_loading_index < len(users):
            # Show loading indicator
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: #f8f9ff; border-radius: 15px; margin: 1rem 0;">
                <div class="streaming-indicator">
                    🔍 Đang phân tích người dùng tiếp theo
                    <div class="loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Auto-load next user after delay
            time.sleep(2)  # Streaming delay
            
            current_user_data = users[st.session_state.current_loading_index]
            
            # Add user to loaded list
            st.session_state.loaded_users.append(current_user_data)
            
            # Categorize user based on risk
            if current_user_data.get('suicide_risk') == 1:
                st.session_state.high_risk_users.append(current_user_data)
            else:
                st.session_state.low_risk_users.append(current_user_data)
            
            st.session_state.current_loading_index += 1
            
            # Check if completed
            if st.session_state.current_loading_index >= len(users):
                st.session_state.streaming_completed = True
            
            st.rerun()
    
    elif st.session_state.streaming_completed:
        # Completion message
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2ecc71, #27ae60); color: white; 
                   padding: 1.5rem 2rem; border-radius: 20px; text-align: center; 
                   margin: 2rem 0; box-shadow: 0 8px 25px rgba(46, 204, 113, 0.3);">
            <h3>🎉 Stream hoàn tất!</h3>
            <p>Đã phân tích xong tất cả {len(users)} người dùng</p>
            <p>Phát hiện {len(st.session_state.high_risk_users)} người dùng có nguy cơ cao và {len(st.session_state.low_risk_users)} người dùng nguy cơ thấp</p>
        </div>
        """, unsafe_allow_html=True)

else:
    st.error("Không thể tải dữ liệu. Vui lòng kiểm tra:")
    st.write("1. Flask server đang chạy trên localhost:5000")
    st.write("2. File data/user_his.csv tồn tại")
    st.write("3. API /view_user_history hoạt động bình thường")

