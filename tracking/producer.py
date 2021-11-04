import pika

def publish(message):
   params = pika.URLParameters('amqp://guest:guest@rabbitmq:5672')
   connection = pika.BlockingConnection(params)
   channel = connection.channel()

   queue_name = "tracking-order-queue"

   channel.queue_declare(queue=queue_name, durable=True)
   channel.basic_publish(
                   exchange='',
                   routing_key=queue_name,
                   body=message,
                   properties=pika.BasicProperties(
                      delivery_mode = 2,
                   ))
   connection.close()