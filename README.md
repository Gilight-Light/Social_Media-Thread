# Social Media Crawler & Mental Health Analysis System

A comprehensive system for crawling social media posts from Threads, analyzing mental health indicators, and providing real-time insights through interactive dashboards.

## 🎯 Features

- **🕷️ Automated Crawling**: Scrape Threads posts using Playwright with anti-detection
- **🧠 Mental Health Analysis**: AI-powered detection of depression and anxiety indicators
- **📊 Real-time Dashboard**: Live streaming analysis with Streamlit
- **⚙️ Workflow Management**: Automated processes with Apache Airflow
- **🔄 Data Streaming**: Real-time processing with Apache Kafka
- **🔒 Privacy Protection**: Automatic username anonymization
- **📈 Analytics**: Comprehensive statistics and visualizations

## 📁 Project Structure

```
social/
├── 🐍 app.py                         # Flask API server
├── 📊 streamlit.py                   # Streamlit dashboard
├── 🔄 kafka_streaming.py             # Kafka streaming service
├── 🐳 docker-compose.yml             # Docker orchestration
├── 📋 requirements.txt               # Python dependencies
├── 🗂️ dags/
│   └── social_crawler_dag.py         # Airflow workflows
├── 📁 data/
│   ├── main_posts.csv                # Main posts data
│   ├── user_his.csv                  # User history
│   ├── filtered_posts.csv            # Filtered results
│   └── all_users_history_data.jsonl  # Raw user data
├── 🎨 templates/
│   └── index.html                    # Web interface
├── 🎯 static/
│   ├── css/style.css                 # Stylesheets
│   └── js/main.js                    # JavaScript
└── 🧵 thread/
    ├── scrape_profile.py             # Profile scraper
    ├── scrape_thread.py              # Thread scraper
    ├── crawl_main_posts.py           # Main post crawler
    ├── crawl_users_data.py           # User data crawler
    └── crawl_user_history.py         # User history crawler
```

## 🚀 Quick Start

### Option 1: Docker Setup (Recommended)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd social

# 2. Start all services with one command
docker-compose up -d

# 3. Wait for services to initialize (2-3 minutes)
docker-compose logs -f

# 4. Access applications
echo "🌐 Flask Dashboard: http://localhost:5000"
echo "📊 Streamlit App: http://localhost:8501"
echo "⚙️ Airflow UI: http://localhost:8080 (admin/admin)"
```

### Option 2: Manual Setup

```bash
# 1. Clone and setup environment
git clone <your-repo-url>
cd social
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Create data directory
mkdir -p data logs

# 4. Start services
python app.py &
streamlit run streamlit.py &
```

## 🌐 Application Access

| Service | URL | Credentials | Description |
|---------|-----|-------------|-------------|
| **Flask Dashboard** | http://localhost:5000 | - | Main control panel |
| **Streamlit App** | http://localhost:8501 | - | Real-time analytics |
| **Airflow Web UI** | http://localhost:8080 | admin/admin | Workflow management |
| **Kafka UI** | http://localhost:8081 | - | Stream monitoring |

## 📋 Prerequisites

- **Python 3.10+**
- **Docker & Docker Compose** (for containerized setup)
- **8GB+ RAM** (recommended)
- **Internet connection** (for crawling)

## 💡 Usage Guide

### 1. Flask Dashboard (Main Interface)

```bash
# Access: http://localhost:5000
```

**Key Features:**
- 📈 **Data Status**: View current data statistics
- 🔍 **Filter Posts**: Filter by symptom groups (depression, anxiety, insomnia)
- 👥 **Crawl Users**: Extract user profiles from filtered posts
- 📊 **View Results**: Analyze crawled data and download reports

**Sample Workflow:**
1. Upload your CSV data to `data/main_posts.csv`
2. Click "Filter Posts" → Select symptom group
3. Click "Start Users Crawl" → Monitor progress
4. Download results as CSV/JSON

### 2. Streamlit Real-time Dashboard

```bash
# Access: http://localhost:8501
```

**Features:**
- 🔴 **Live Streaming**: Real-time user analysis
- 🎯 **Risk Classification**: Automatic categorization (High/Low risk)
- 📊 **Progress Tracking**: Live updates with progress bars
- 🔍 **Detailed Analysis**: Expandable user cards with post analysis

**How to Use:**
1. Click "🚀 Bắt đầu Stream" to start analysis
2. Watch real-time progress and classifications
3. Expand user cards for detailed insights
4. Use sidebar filters for specific analysis

### 3. Airflow Workflows

```bash
# Access: http://localhost:8080 (admin/admin)
```

**Automated Workflows:**
- 🕰️ **Scheduled Crawling**: Every 6 hours
- 📊 **Data Processing**: Automatic analysis pipeline
- 🔄 **Error Handling**: Retry mechanisms and logging

## 📊 Data Format

### Input Data (main_posts.csv)
```csv
username,text,timestamp,url,symptom_group,keyword,label
user123,"Feeling sad today...",2024-01-15 14:30,https://threads.net/@user123/post/123,mood_depressed,buồn,1
user456,"Can't sleep at 3am",2024-01-15 03:00,https://threads.net/@user456/post/456,insomnia,mất ngủ,0
```

### Output Data Structure
```json
{
  "username": "user123_***",
  "risk_level": "high",
  "posts_analyzed": 25,
  "depression_indicators": ["sadness", "hopelessness"],
  "confidence_score": 0.85,
  "last_activity": "2024-01-15T14:30:00Z"
}
```

## ⚙️ Configuration

### Environment Variables
```bash
# Create .env file
cat > .env << EOF
FLASK_ENV=development
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
EOF
```

### Docker Services
```yaml
# Included services:
- flask-app          # API server
- streamlit-app      # Dashboard
- airflow-webserver  # Workflow UI
- airflow-scheduler  # Task scheduler
- kafka              # Message streaming
- zookeeper          # Kafka coordination
- postgres           # Database
- redis              # Caching
```

## 🔧 API Reference

### Flask Endpoints
```bash
# Data Management
GET  /                          # Dashboard home
GET  /api/data_summary          # Data statistics
POST /filter_posts              # Filter posts by criteria
POST /start_users_crawl         # Start user crawling

# User Analysis
GET  /view_user_history         # View user history
POST /export_users_data         # Export analysis results
GET  /download/<file_type>      # Download data files

# System
GET  /api/system_info           # System status
GET  /task_status/<task_id>     # Task progress
```

### Streamlit Features
- **Real-time Processing**: Live data analysis
- **Interactive Filters**: Dynamic content filtering
- **Export Functions**: CSV/JSON download
- **Progress Monitoring**: Live task tracking

## 🛠️ Development

### Adding New Features

```bash
# 1. Add new crawler
cp thread/crawl_template.py thread/crawl_new_feature.py

# 2. Add to Flask routes
# Edit app.py - add new endpoint

# 3. Add to Streamlit
# Edit streamlit.py - add new analysis

# 4. Add to Airflow DAG
# Edit dags/social_crawler_dag.py
```

### Testing

```bash
# Run tests
python -m pytest tests/

# Test specific component
python thread/scrape_profile.py --test
python thread/crawl_users_data.py --test
```

## 📈 Performance & Monitoring

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB+ for full stack
- **Storage**: 10GB+ for data
- **Network**: Stable internet for crawling

### Monitoring Commands
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f flask-app
docker-compose logs -f streamlit-app

# Monitor resources
docker stats
```

### Performance Tips
- Use Docker for better resource management
- Monitor Kafka lag for streaming performance
- Set appropriate crawling delays to avoid rate limits
- Regular data cleanup to prevent storage issues

## 🔒 Privacy & Security

### Data Protection
- **Username Anonymization**: All usernames automatically masked
- **Data Encryption**: Sensitive data hashed with MD5
- **Access Control**: No external access to raw personal data
- **GDPR Compliance**: Built-in privacy protection

### Security Features
```python
# Automatic username masking
def mask_username(username):
    return f"{username[:3]}{'*' * (len(username) - 3)}"

# Data encryption
import hashlib
user_hash = hashlib.md5(username.encode()).hexdigest()[:8]
```

## 🐛 Troubleshooting

### Common Issues

**1. Port Conflicts**
```bash
# Change ports in docker-compose.yml
ports:
  - "5001:5000"  # Flask
  - "8502:8501"  # Streamlit
```

**2. Memory Issues**
```bash
# Increase Docker memory
docker-compose down
# Increase Docker Desktop memory to 8GB+
docker-compose up -d
```

**3. Permission Issues**
```bash
# Fix data directory permissions
sudo chown -R $USER:$USER data/
chmod -R 755 data/
```

**4. Kafka Connection Issues**
```bash
# Restart Kafka services
docker-compose restart kafka zookeeper
# Wait for services to fully start
sleep 30
```

### Debug Mode
```bash
# Enable debug logging
export FLASK_DEBUG=1
export STREAMLIT_LOGGER_LEVEL=DEBUG

# Run with verbose output
python app.py --debug
streamlit run streamlit.py --logger.level=debug
```

### Health Checks
```bash
# Test Flask API
curl http://localhost:5000/api/system_info

# Test Streamlit
curl http://localhost:8501/healthz

# Test Kafka
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

## 📊 Sample Data

The system includes sample data for testing:

- **6,000+ posts** from Vietnamese social media users
- **500+ unique user profiles**
- **Mental health keywords** in Vietnamese
- **Depression/anxiety indicators** with confidence scores

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

```bash
# Development workflow
git checkout -b feature/new-analysis
git commit -m "Add new analysis feature"
git push origin feature/new-analysis
# Create PR on GitHub
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Playwright** for web scraping capabilities
- **Streamlit** for beautiful dashboards
- **Apache Airflow** for workflow orchestration
- **Apache Kafka** for real-time streaming
- **Bootstrap** for responsive UI design

## 📞 Support

### Getting Help
- 📖 **Documentation**: Check this README
- 🐛 **Issues**: Open GitHub issue
- 💬 **Discussions**: Use GitHub Discussions
- 📧 **Email**: [your-email@domain.com]

### Quick Links
- 🔗 [Project Repository](https://github.com/your-username/social)
- 📚 [API Documentation](docs/api.md)
- 🎥 [Video Tutorial](https://youtube.com/watch?v=example)
- 📊 [Live Demo](https://demo.yourproject.com)

---

⭐ **If this project helps you, please give it a star!** ⭐

---

**Made with ❤️ for mental health awareness and social media analysis**
