import json
import pika
import db

def main():
  params = pika.URLParameters('amqp://guest:guest@rabbitmq:5672')
  connection = pika.BlockingConnection(params)
  channel = connection.channel()

  queue_name = 'tracking-order-queue'
  channel.queue_declare(queue=queue_name, durable=True)

  def callback(ch, method, properties, body):
    json_body = json.loads(body.decode())
    event_type = json_body.get("event-type")
    data = json_body.get("data")
    print(123)
    if (event_type == "order-updated"):
      print(data)
      order = db.access_order()
      order.insert_one(data)

  channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
  channel.start_consuming()

if __name__ == '__main__':
  main()