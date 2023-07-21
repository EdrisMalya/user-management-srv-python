import json
import os

import pika


class Publisher:
    def publish(self, queue_name, exchange_name, method, message, routing_key):
        connection = self.create_connection()
        # Create a new channel with the next available channel number or pass
        # in a channel number to use channel =
        # Open the channel
        channel = connection.channel()

        # Creates an exchange if it does not already exist, and if
        # the exchange exists,
        # verifies that it is of the correct and expected class.
        channel.exchange_declare(
            exchange=exchange_name, exchange_type="direct", durable=True
        )

        # Declare the queue
        channel.queue_declare(
            queue=queue_name, durable=True, exclusive=False, auto_delete=False
        )

        # Turn on delivery confirmations
        channel.confirm_delivery()

        # Send a message
        properties = pika.BasicProperties(method)
        try:
            channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=properties,
                mandatory=True,
            )
            channel.close()
            print("Message publish was confirmed")
        except pika.exceptions.UnroutableError as exc:
            print(exc)
            print("Message could not be confirmed")
        except pika.exceptions.ChannelWrongStateError:
            print("Channel is Closed")

    # Create new connection
    def create_connection(self):
        # params = pika.URLParameters("amqp://guest:guest@10.0.0.95:5672/%2F?heartbeat=30")
        if os.getenv('FASTAPI_ENV') == 'production':
            params = pika.ConnectionParameters(
                host="10.0.0.62", heartbeat=600, blocked_connection_timeout=300
            )
        elif os.getenv('FASTAPI_ENV') == 'development':
            params = pika.ConnectionParameters(
                host="10.0.0.30", heartbeat=600, blocked_connection_timeout=300
            )
        else:
            params = pika.ConnectionParameters(
                host="localhost", heartbeat=600, blocked_connection_timeout=300
            )
        return pika.BlockingConnection(params)


publisher = Publisher()
