import json
import time
import logging
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from datetime import datetime
from typing import Dict, Any
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaStreamingService:
    def __init__(self, bootstrap_servers='localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.consumer = None
        
    def create_producer(self):
        """Create Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8') if k else None,
                acks='all',
                retries=3,
                batch_size=16384,
                linger_ms=10,
                buffer_memory=33554432
            )
            logger.info("Kafka producer created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create Kafka producer: {e}")
            return False
    
    def create_consumer(self, topics, group_id='social-crawler-group'):
        """Create Kafka consumer"""
        try:
            self.consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000
            )
            logger.info(f"Kafka consumer created for topics: {topics}")
            return True
        except Exception as e:
            logger.error(f"Failed to create Kafka consumer: {e}")
            return False
    
    def send_crawl_progress(self, task_id: str, progress_data: Dict[str, Any]):
        """Send crawling progress to Kafka topic"""
        if not self.producer:
            if not self.create_producer():
                return False
        
        topic = 'crawl-progress'
        message = {
            'task_id': task_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'progress',
            **progress_data
        }
        
        try:
            future = self.producer.send(topic, key=task_id, value=message)
            future.get(timeout=10)  # Wait for confirmation
            logger.info(f"Sent progress update for task {task_id}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to send message to Kafka: {e}")
            return False
    
    def send_crawl_result(self, task_id: str, result_data: Dict[str, Any]):
        """Send crawling result to Kafka topic"""
        if not self.producer:
            if not self.create_producer():
                return False
        
        topic = 'crawl-results'
        message = {
            'task_id': task_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'result',
            **result_data
        }
        
        try:
            future = self.producer.send(topic, key=task_id, value=message)
            future.get(timeout=10)
            logger.info(f"Sent crawl result for task {task_id}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to send result to Kafka: {e}")
            return False
    
    def send_user_data(self, username: str, user_data: Dict[str, Any]):
        """Send user data to Kafka topic"""
        if not self.producer:
            if not self.create_producer():
                return False
        
        topic = 'user-data'
        message = {
            'username': username,
            'timestamp': datetime.now().isoformat(),
            'type': 'user_data',
            **user_data
        }
        
        try:
            future = self.producer.send(topic, key=username, value=message)
            future.get(timeout=10)
            logger.info(f"Sent user data for {username}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to send user data to Kafka: {e}")
            return False
    
    def consume_messages(self, topics, callback_function):
        """Consume messages from Kafka topics"""
        if not self.create_consumer(topics):
            return False
        
        logger.info(f"Starting to consume messages from topics: {topics}")
        
        try:
            for message in self.consumer:
                callback_function(message.topic, message.key, message.value)
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
        finally:
            if self.consumer:
                self.consumer.close()
    
    def close(self):
        """Close producer and consumer"""
        if self.producer:
            self.producer.close()
        if self.consumer:
            self.consumer.close()
        logger.info("Kafka connections closed")

# Example usage and testing functions
def example_progress_callback(topic, key, value):
    """Example callback for handling progress messages"""
    logger.info(f"Received from {topic}: {key} -> {value}")

def example_streaming_crawler():
    """Example of how to use Kafka streaming with crawling"""
    kafka_service = KafkaStreamingService()
    
    # Simulate crawling process with Kafka streaming
    def simulate_crawl():
        task_id = f"crawl_{int(time.time())}"
        
        # Send start message
        kafka_service.send_crawl_progress(task_id, {
            'status': 'started',
            'message': 'Starting crawl process',
            'progress': 0
        })
        
        # Simulate crawling steps
        for i in range(1, 6):
            time.sleep(2)  # Simulate work
            
            # Send progress update
            kafka_service.send_crawl_progress(task_id, {
                'status': 'in_progress',
                'message': f'Processing step {i}/5',
                'progress': i * 20
            })
            
            # Simulate finding user data
            if i == 3:
                kafka_service.send_user_data(f"user_{i}", {
                    'posts_found': 15,
                    'risk_score': 0.7,
                    'status': 'high_risk'
                })
        
        # Send completion message
        kafka_service.send_crawl_result(task_id, {
            'status': 'completed',
            'message': 'Crawl completed successfully',
            'total_users': 5,
            'total_posts': 75
        })
    
    # Start crawler in separate thread
    crawler_thread = threading.Thread(target=simulate_crawl)
    crawler_thread.start()
    
    # Start consumer to monitor progress
    try:
        kafka_service.consume_messages(
            ['crawl-progress', 'crawl-results', 'user-data'],
            example_progress_callback
        )
    except KeyboardInterrupt:
        logger.info("Streaming interrupted")
    finally:
        kafka_service.close()
        crawler_thread.join()

def test_kafka_connection():
    """Test Kafka connection"""
    kafka_service = KafkaStreamingService()
    
    # Test producer
    if kafka_service.create_producer():
        logger.info("✅ Kafka producer connection successful")
        
        # Send test message
        test_message = {
            'test': True,
            'message': 'Kafka connection test',
            'timestamp': datetime.now().isoformat()
        }
        
        kafka_service.send_crawl_progress('test_task', test_message)
    else:
        logger.error("❌ Kafka producer connection failed")
    
    # Test consumer
    if kafka_service.create_consumer(['crawl-progress']):
        logger.info("✅ Kafka consumer connection successful")
    else:
        logger.error("❌ Kafka consumer connection failed")
    
    kafka_service.close()

if __name__ == "__main__":
    # Test Kafka connection first
    print("Testing Kafka connection...")
    test_kafka_connection()
    
    # Run streaming example
    print("\nRunning streaming example...")
    example_streaming_crawler()