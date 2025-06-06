import streamlit as st
import pandas as pd
import requests
import json
import time
import random
from datetime import datetime
import numpy as np

# Cấu hình trang
st.set_page_config(
    page_title="Social Media Suicide Risk Analysis",
    page_icon="🧠",
    layout="wide"
)

# CSS tùy chỉnh - Modern & Professional
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
    
    .user-list-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 2rem 0;
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
        cursor: pointer;
    }
    
    .user-card:hover {
        transform: translateX(5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }
    
    .user-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(135deg, #667eea, #764ba2);
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
    
    .user-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    
    .user-info {
        display: flex;
        align-items: center;
        flex: 1;
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
    
    .user-details h3 {
        margin: 0;
        color: #2c3e50;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    .user-meta {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }
    
    .risk-badge-mini-high {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
        padding: 6px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
        display: inline-flex;
        align-items: center;
        box-shadow: 0 3px 10px rgba(231, 76, 60, 0.3);
        animation: pulse 2s infinite;
    }
    
    .risk-badge-mini-low {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        color: white;
        padding: 6px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
        display: inline-flex;
        align-items: center;
        box-shadow: 0 3px 10px rgba(39, 174, 96, 0.3);
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .posts-count {
        background: #667eea;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 1rem;
    }
    
    .click-hint {
        color: #667eea;
        font-size: 0.8rem;
        font-style: italic;
        margin-top: 0.5rem;
        text-align: right;
    }
    
    .loading-new-user {
        background: linear-gradient(145deg, #f8f9ff, #ffffff);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        border: 2px dashed #667eea;
        margin: 1rem 0;
        animation: loadingPulse 1.5s ease-in-out infinite;
    }
    
    @keyframes loadingPulse {
        0%, 100% { opacity: 0.7; }
        50% { opacity: 1; }
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
    
    .detailed-modal {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        max-height: 80vh;
        overflow-y: auto;
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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🧠 Social Media Suicide Risk Analysis</h1>
    <p>Phân tích ý định tự sát qua bài đăng Threads - Real-time Streaming Analysis</p>
</div>
""", unsafe_allow_html=True)

# Hàm tải dữ liệu
@st.cache_data(ttl=300)
def load_data():
    try:
        response = requests.get("http://localhost:5000/view_user_history")
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data['data'])
        else:
            return load_sample_data()
    except Exception as e:
        return load_sample_data()

def load_sample_data():
    """Dữ liệu mẫu từ file đã cung cấp"""
    sample_data = [
        {
            "post_text": "Sao cuộc sống chán z v momm",
            "timestamp": "26/05/2025 11:13",
            "url": "https://www.threads.net/@_tha.vwu/post/DKGlvVaSaoj",
            "username": "_tha.vwu"
        },
        {
            "post_text": '"Nếu không có ai đối xử ngọt ngào với bạn, bạn vẫn có thể tự đối xử ngọt ngào với bản thân mình". "Love yourself" Yêu bản thân.',
            "timestamp": "01/07/2024 22:14",
            "url": "https://www.threads.net/@_nhw.taw_/post/C84n3NzS1iV",
            "username": "_nhw.taw_"
        },
        {
            "post_text": '"Cuối cùng rồi sẽ có một ngày bạn trở nên bình tĩnh. Giống như người ngoài cuộc, nhìn lại những câu chuyện xưa cũ của chính mình rồi lắc đầu cười trong vô thức".',
            "timestamp": "29/06/2024 22:47",
            "url": "https://www.threads.net/@_nhw.taw_/post/C8ziDHnSR2H",
            "username": "_nhw.taw_"
        },
        {
            "post_text": "Best seller nhà e thì cứ tự tin là pizza với gà sốt . Ngoài ra các món khác thuộc top Á hậu thôi.",
            "timestamp": "31/05/2025 12:41",
            "url": "https://www.threads.net/@nhungdua.6/post/DKTnwxDTLJT",
            "username": "nhungdua.6"
        },
        {
            "post_text": "Phải trải qua sóng gió, mới trân trọng những tháng ngày bình yên..",
            "timestamp": "19/06/2024 14:02",
            "url": "https://www.threads.net/@_nhw.taw_/post/C8Y1-4_yv5l",
            "username": "_nhw.taw_"
        },
        {
            "post_text": "Mệt mỏi quá, không biết còn bao lâu nữa mới hết.",
            "timestamp": "15/06/2024 20:30",
            "url": "https://www.threads.net/@duanbbo/post/C8X1234",
            "username": "duanbbo"
        },
        {
            "post_text": "Đêm nay lại thức trắng, tâm trạng không ổn lắm.",
            "timestamp": "12/06/2024 03:15",
            "url": "https://www.threads.net/@_barelavvel_/post/C8W5678",
            "username": "_barelavvel_"
        },
        {
            "post_text": "Cảm giác như không ai hiểu mình, thật sự rất cô đơn.",
            "timestamp": "10/06/2024 22:45",
            "url": "https://www.threads.net/@lalucifer.666/post/C8V9012",
            "username": "lalucifer.666"
        }
    ]
    return pd.DataFrame(sample_data)

def analyze_suicide_risk(posts_text):
    """Simulate AI analysis based on post content"""
    # Keywords that might indicate higher risk
    high_risk_keywords = ['chán', 'mệt mỏi', 'cô đơn', 'không ai hiểu', 'thức trắng', 'tâm trạng không ổn']
    
    # Check if any high-risk keywords appear in posts
    all_text = ' '.join(posts_text).lower()
    risk_score = sum(1 for keyword in high_risk_keywords if keyword in all_text)
    
    # Higher chance of risk if more keywords found
    if risk_score >= 2:
        return random.choices([0, 1], weights=[30, 70])[0]  # 70% chance of risk
    elif risk_score == 1:
        return random.choices([0, 1], weights=[60, 40])[0]  # 40% chance of risk
    else:
        return random.choices([0, 1], weights=[85, 15])[0]  # 15% chance of risk

def get_user_stats(df, username):
    """Lấy thống kê của user"""
    user_posts = df[df['username'] == username]
    
    try:
        user_posts['timestamp_dt'] = pd.to_datetime(user_posts['timestamp'], format='%d/%m/%Y %H:%M')
        first_post = user_posts['timestamp_dt'].min().strftime('%d/%m/%Y %H:%M')
        last_post = user_posts['timestamp_dt'].max().strftime('%d/%m/%Y %H:%M')
    except:
        first_post = user_posts['timestamp'].iloc[0] if len(user_posts) > 0 else "N/A"
        last_post = user_posts['timestamp'].iloc[-1] if len(user_posts) > 0 else "N/A"
    
    return {
        'total_posts': len(user_posts),
        'first_post': first_post,
        'last_post': last_post,
        'posts': user_posts['post_text'].tolist(),
        'timestamps': user_posts['timestamp'].tolist(),
        'urls': user_posts['url'].tolist()
    }

# Load data
df = load_data()

if df is not None and not df.empty:
    # Khởi tạo session state
    if 'loaded_users' not in st.session_state:
        st.session_state.loaded_users = []
        st.session_state.streaming_started = False
        st.session_state.streaming_completed = False
        st.session_state.current_loading_index = 0
        st.session_state.all_users = df['username'].unique().tolist()
        st.session_state.show_user_details = {}
    
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
            st.rerun()
    
    with col3:
        if st.button("🔄 Reset Stream", type="secondary"):
            st.session_state.loaded_users = []
            st.session_state.streaming_started = False
            st.session_state.streaming_completed = False
            st.session_state.current_loading_index = 0
            st.session_state.show_user_details = {}
            st.rerun()
    
    # Statistics Overview
    high_risk_count = len([u for u in st.session_state.loaded_users if u.get('suicide_risk') == 1])
    
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-card">
            <span class="stat-number">{len(users)}</span>
            <div class="stat-label">Tổng số người dùng</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">{len(st.session_state.loaded_users)}</span>
            <div class="stat-label">Đã phân tích</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">{len(df)}</span>
            <div class="stat-label">Tổng bài đăng</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">{high_risk_count}</span>
            <div class="stat-label">Có nguy cơ cao</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress Bar
    if len(users) > 0:
        progress = len(st.session_state.loaded_users) / len(users)
        st.progress(progress, text=f"Streaming: {len(st.session_state.loaded_users)}/{len(users)} người dùng ({progress*100:.1f}%)")
    
    # Main Streaming Area
    st.markdown("## 📊 Live User Analysis Stream")
    
    user_list_container = st.container()
    
    with user_list_container:
        # Display loaded users
        for i, user_data in enumerate(st.session_state.loaded_users):
            username = user_data['username']
            suicide_risk = user_data['suicide_risk']
            stats = user_data['stats']
            
            # Risk badge
            if suicide_risk == 1:
                risk_badge = '<div class="risk-badge-mini-high">🚨 HIGH RISK</div>'
            else:
                risk_badge = '<div class="risk-badge-mini-low">✅ LOW RISK</div>'
            
            # User card with click functionality
            user_initial = username[0].upper() if username else "U"
            
            # Create expandable section for each user
            with st.expander(f"👤 @{username} - {stats['total_posts']} bài đăng", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="padding: 1rem 0;">
                        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                            <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #667eea, #764ba2); 
                                      border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                                      color: white; font-size: 1.5rem; font-weight: bold; margin-right: 1rem;">
                                {user_initial}
                            </div>
                            <div>
                                <h3 style="margin: 0; color: #2c3e50;">@{username}</h3>
                                <p style="margin: 0.5rem 0; color: #7f8c8d;">
                                    📊 {stats['total_posts']} bài đăng | 📅 {stats['first_post']} - {stats['last_post']}
                                </p>
                            </div>
                        </div>
                        {risk_badge}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"📝 Xem chi tiết", key=f"detail_{username}_{i}"):
                        st.session_state.show_user_details[username] = not st.session_state.show_user_details.get(username, False)
                        st.rerun()
                
                # Show detailed posts if requested
                if st.session_state.show_user_details.get(username, False):
                    st.markdown("### 📝 Chi tiết bài đăng")
                    
                    for j, (post, timestamp, url) in enumerate(zip(stats['posts'], stats['timestamps'], stats['urls'])):
                        st.markdown(f"""
                        <div class="post-container">
                            <div class="post-header">
                                <span class="post-number">Bài #{j+1}</span>
                                <span class="post-timestamp">📅 {timestamp}</span>
                            </div>
                            <div class="post-content">"{post}"</div>
                            <div style="text-align: right; margin-top: 1rem;">
                                <a href="{url}" target="_blank" style="color: #667eea; text-decoration: none; font-weight: 500;">
                                    🔗 Xem bài gốc →
                                </a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Streaming logic
        if st.session_state.streaming_started and not st.session_state.streaming_completed:
            if st.session_state.current_loading_index < len(users):
                # Show loading indicator for next user
                st.markdown("""
                <div class="loading-new-user">
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
                
                current_username = users[st.session_state.current_loading_index]
                user_stats = get_user_stats(df, current_username)
                suicide_risk = analyze_suicide_risk(user_stats['posts'])
                
                # Add user to loaded list
                st.session_state.loaded_users.append({
                    'username': current_username,
                    'suicide_risk': suicide_risk,
                    'stats': user_stats
                })
                
                st.session_state.current_loading_index += 1
                
                # Check if completed
                if st.session_state.current_loading_index >= len(users):
                    st.session_state.streaming_completed = True
                
                st.rerun()
        
        elif st.session_state.streaming_completed:
            # Completion message
            st.markdown("""
            <div style="background: linear-gradient(135deg, #2ecc71, #27ae60); color: white; 
                       padding: 1.5rem 2rem; border-radius: 20px; text-align: center; 
                       margin: 2rem 0; box-shadow: 0 8px 25px rgba(46, 204, 113, 0.3);">
                <h3>🎉 Stream hoàn tất!</h3>
                <p>Đã phân tích xong tất cả {len(users)} người dùng</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Final summary
            high_risk_users = [u for u in st.session_state.loaded_users if u['suicide_risk'] == 1]
            low_risk_users = [u for u in st.session_state.loaded_users if u['suicide_risk'] == 0]
            
            if high_risk_users:
                st.markdown("### 🚨 Tổng kết người dùng có nguy cơ cao:")
                for user in high_risk_users:
                    st.error(f"⚠️ @{user['username']} - {user['stats']['total_posts']} bài đăng")
            
            if st.session_state.loaded_users:
                risk_rate = (len(high_risk_users) / len(st.session_state.loaded_users)) * 100
                st.metric(
                    "📈 Tỷ lệ nguy cơ tổng thể", 
                    f"{risk_rate:.1f}%",
                    delta=f"{len(high_risk_users)} / {len(st.session_state.loaded_users)} người dùng"
                )

else:
    st.error("❌ Không thể tải dữ liệu từ API")
    st.info("💡 Đảm bảo server Flask đang chạy tại http://localhost:5000")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem; background: #f8f9ff; border-radius: 15px; margin-top: 2rem;">
    <h4>⚠️ Lưu ý quan trọng</h4>
    <p>Đây là hệ thống nghiên cứu mô phỏng cho mục đích học thuật và phát triển công nghệ.</p>
    <p>Kết quả phân tích được tạo bởi thuật toán mô phỏng, không phải AI thực tế.</p>
    <p><strong>Trong thực tế, việc phát hiện ý định tự sát cần sự can thiệp của chuyên gia tâm lý.</strong></p>
</div>
""", unsafe_allow_html=True)