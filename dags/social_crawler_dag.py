from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

# Add project directory to Python path
sys.path.append('/opt/airflow/project')

# Import your crawling functions
from kafka_streaming_example import KafkaStreamingService

default_args = {
    'owner': 'social-crawler',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'social_media_crawler',
    default_args=default_args,
    description='Social Media Crawler with Kafka Streaming',
    schedule_interval=timedelta(hours=6),  # Run every 6 hours
    catchup=False,
    tags=['social', 'crawler', 'kafka'],
)

def crawl_main_posts_task(**context):
    """Task to crawl main posts using crawl_main_posts.py"""
    import subprocess
    import json
    
    # Initialize Kafka service
    kafka_service = KafkaStreamingService(bootstrap_servers='kafka:29092')
    task_id = f"crawl_main_posts_{int(datetime.now().timestamp())}"
    
    try:
        # Send start notification
        kafka_service.send_crawl_progress(task_id, {
            'status': 'started',
            'message': 'Starting main posts crawl',
            'progress': 0,
            'task_type': 'main_posts'
        })
        
        # Define keywords to crawl
        keywords = [
            '3h sáng vẫn chưa ngủ',
            'buồn không tả nổi',
            'bản thân tệ quá ghê',
            'bế tắc',
            'bị mọi người bỏ rơi'
        ]
        
        total_keywords = len(keywords)
        total_posts = 0
        
        for i, keyword in enumerate(keywords):
            # Send progress update
            progress = (i / total_keywords) * 100
            kafka_service.send_crawl_progress(task_id, {
                'status': 'in_progress',
                'message': f'Crawling keyword: {keyword}',
                'progress': progress,
                'current_keyword': keyword,
                'keywords_completed': i,
                'total_keywords': total_keywords
            })
            
            # Run crawl_main_posts.py for each keyword
            result = subprocess.run([
                'python', '/opt/airflow/project/crawl_main_posts.py', keyword
            ], capture_output=True, text=True, cwd='/opt/airflow/project')
            
            if result.returncode == 0:
                print(f"Successfully crawled keyword: {keyword}")
                # You can parse the output to get the number of posts
                # For now, we'll assume each keyword yields some posts
                total_posts += 10  # Placeholder
            else:
                print(f"Error crawling keyword {keyword}: {result.stderr}")
                kafka_service.send_crawl_progress(task_id, {
                    'status': 'error',
                    'message': f'Error crawling keyword: {keyword}',
                    'error': result.stderr
                })
        
        # Send completion notification
        kafka_service.send_crawl_result(task_id, {
            'status': 'completed',
            'message': f'Main posts crawl completed. Total posts: {total_posts}',
            'total_posts': total_posts,
            'keywords_processed': total_keywords,
            'output_file': '/opt/airflow/data/main_posts.csv'
        })
        
        return {
            'task_id': task_id,
            'status': 'completed',
            'total_posts': total_posts,
            'keywords_processed': total_keywords
        }
        
    except Exception as e:
        # Send error notification
        kafka_service.send_crawl_progress(task_id, {
            'status': 'error',
            'message': f'Error in main posts crawl: {str(e)}',
            'error': str(e)
        })
        raise e
    finally:
        kafka_service.close()

def process_posts_task(**context):
    """Task to process and label posts"""
    import pandas as pd
    import numpy as np
    
    # Initialize Kafka service
    kafka_service = KafkaStreamingService(bootstrap_servers='kafka:29092')
    task_id = f"process_posts_{int(datetime.now().timestamp())}"
    
    try:
        # Send start notification
        kafka_service.send_crawl_progress(task_id, {
            'status': 'started',
            'message': 'Starting posts processing',
            'progress': 0,
            'task_type': 'process_posts'
        })
        
        # Load main posts
        csv_file = '/opt/airflow/data/main_posts.csv'
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"Main posts file not found: {csv_file}")
        
        df = pd.read_csv(csv_file)
        
        # Add label column if not exists
        if 'label' not in df.columns:
            # Simple labeling logic based on keywords
            high_risk_keywords = [
                'buồn không tả nổi', 'bản thân tệ quá ghê', 
                'bị mọi người bỏ rơi', 'bế tắc'
            ]
            
            def assign_label(row):
                text = str(row.get('text', '')).lower()
                keyword = str(row.get('keyword', '')).lower()
                
                # Check if keyword or text contains high-risk indicators
                for risk_keyword in high_risk_keywords:
                    if risk_keyword in keyword or risk_keyword in text:
                        return 1  # High risk
                
                return 0  # Low risk
            
            df['label'] = df.apply(assign_label, axis=1)
            
            # Save updated CSV
            df.to_csv(csv_file, index=False)
            
            # Send progress update
            kafka_service.send_crawl_progress(task_id, {
                'status': 'completed',
                'message': 'Posts processing completed',
                'progress': 100,
                'total_posts': len(df),
                'high_risk_posts': len(df[df['label'] == 1]),
                'low_risk_posts': len(df[df['label'] == 0])
            })
            
            return {
                'task_id': task_id,
                'status': 'completed',
                'total_posts': len(df),
                'high_risk_posts': len(df[df['label'] == 1]),
                'low_risk_posts': len(df[df['label'] == 0])
            }
        
    except Exception as e:
        kafka_service.send_crawl_progress(task_id, {
            'status': 'error',
            'message': f'Error in posts processing: {str(e)}',
            'error': str(e)
        })
        raise e
    finally:
        kafka_service.close()

def send_completion_notification(**context):
    """Send final completion notification"""
    kafka_service = KafkaStreamingService(bootstrap_servers='kafka:29092')
    
    try:
        kafka_service.send_crawl_result('dag_completion', {
            'status': 'dag_completed',
            'message': 'Social media crawler DAG completed successfully',
            'timestamp': datetime.now().isoformat(),
            'dag_id': 'social_media_crawler'
        })
    finally:
        kafka_service.close()

# Define tasks
crawl_main_posts = PythonOperator(
    task_id='crawl_main_posts',
    python_callable=crawl_main_posts_task,
    dag=dag,
)

process_posts = PythonOperator(
    task_id='process_posts',
    python_callable=process_posts_task,
    dag=dag,
)

send_notification = PythonOperator(
    task_id='send_completion_notification',
    python_callable=send_completion_notification,
    dag=dag,
)

# Create directories task
create_directories = BashOperator(
    task_id='create_directories',
    bash_command='mkdir -p /opt/airflow/data',
    dag=dag,
)

# Set task dependencies
create_directories >> crawl_main_posts >> process_posts >> send_notification