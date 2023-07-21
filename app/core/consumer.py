import os

import pika

if os.getenv('FASTAPI_ENV') == 'production':
    params = pika.URLParameters("amqp://guest:guest@10.0.0.62:5672/%2F?heartbeat=30")
if os.getenv('FASTAPI_ENV') == 'development':
    params = pika.URLParameters("amqp://guest:guest@10.0.0.95:5672/%2F?heartbeat=30")
else:
    params = pika.URLParameters("amqp://guest:guest@localhost:5672/%2F?heartbeat=30")
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue="main-queue", durable=True)
def callback(ch, method, properties, body):
    print("Received in user management")
    print(body)
channel.basic_consume(queue="main-queue", on_message_callback=callback, auto_ack=True)
print("Started Consuming")
channel.start_consuming()
channel.close()
