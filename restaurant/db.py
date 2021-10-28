import os
import pymongo

def access_db():
  try:
    username = os.environ["MONGO_USERNAME"]
    pw = os.environ["MONGO_PASSWORD"]
    host = os.environ["MONGO_SERVER_HOST"]
    port = os.environ["MONGO_SERVER_PORT"]

    uri = f'mongodb://{username}:{pw}@{host}:{port}'
    client = pymongo.MongoClient(uri)
    return client["GoodEat"]
  except:
    print("MongoDB Connection Error")

def access_status():
  return access_db()["status"]