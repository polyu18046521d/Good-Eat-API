import json
from flask import Flask, abort, jsonify, request
import db
import producer
import requests

app = Flask(__name__)

@app.route("/<store_id>", methods=["GET"])
def insert_new_menu(store_id):
  status = dict(db.access_status().find_one({"store_id": store_id}, {"_id": 0}))
  store_info = requests.get(f"http://store-read-api:5001/{store_id}").json()[0]
  menu_info = requests.get(f"http://menu-read-api:5002/{store_id}").json()[0]
  res = store_info | status | menu_info
  return response_helper(200, res)

@app.route("/<store_id>/status", methods=["POST"])
def update_store_status(store_id):
  collection = db.access_status()
  val = dict(request.get_json())['status']
  collection.update_one({ "store_id": store_id }, {"$set": {"status": val}})
  return response_helper(204, "")

@app.route("/<store_id>/menu", methods=["POST"])
def update_store_menu(store_id):
  data = dict(request.get_json())
  producer.publish(json.dumps({
    "event-type": "menu-updated",
    "data": {
      "store_id": store_id,
      "menu": data
    }
  }))
  return response_helper(204, "")

def response_helper(status, json_val, message=None):
  if (message == None):
    if (json_val == []):
      return jsonify({"msg": "Not Found"}), 404
    return jsonify(json_val), status
  else:
    return jsonify({"msg": message}), status

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5004, debug=True)