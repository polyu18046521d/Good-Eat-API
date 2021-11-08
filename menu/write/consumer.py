import json
import pika
import db
import producer

def main():
  params = pika.URLParameters('amqp://guest:guest@rabbitmq:5672')
  connection = pika.BlockingConnection(params)
  channel = connection.channel()

  channel.queue_declare(queue='menu-writer-queue', durable=True)

  def callback(ch, method, properties, body):
    json_body = json.loads(body.decode())
    event_type = json_body.get("event-type")
    data = json_body.get("data")

    if (event_type == "menu-updated"):
      menu = db.access_menu()
      store_id = data["store_id"]
      val = dict(data["menu"])
      menu.update_one({"store_id": store_id}, {"$push": {"menus": val}})
      producer.publish(json.dumps(json_body))
      print("sent from menu writer")

  channel.basic_consume(queue='menu-writer-queue', on_message_callback=callback, auto_ack=True)
  channel.start_consuming()

if __name__ == '__main__':
  main()