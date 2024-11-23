import os
import pika


# Environment variables
RABBITMQ_URL = os.environ.get("RABBITMQ_URL")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD")

# RabbitMQ connection
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_URL, credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue="email_notification")
