import pika

def publish(message):
   params = pika.URLParameters('amqp://guest:guest@rabbitmq:5672')
   connection = pika.BlockingConnection(params)
   channel = connection.channel()

   channel.queue_declare(queue='menu-writer-queue', durable=True)
   channel.basic_publish(
                   exchange='',
                   routing_key='menu-writer-queue',
                   body=message,
                   properties=pika.BasicProperties(
                      delivery_mode = 2,
                   ))
   connection.close()