import json
from flask import Flask, abort, jsonify, request
import db
import producer
import requests
from datetime import datetime

app = Flask(__name__)

@app.route("/<order_id>", methods=["GET"])
def order_query(order_id):
  order_response = requests.get(f"http://order-api:5006/{order_id}")
  if order_response.status_code == 404:
    return response_helper(404, message="Not Found")

  order = order_response.json()[0]
  status = db.access_tracking().find_one({"order_id": order_id}, {"_id": 0})
  res = order | status
  return response_helper(200, res)

@app.route("/", methods=["POST"])
def add_order():
  data = dict(request.get_json())
  data['timestamp'] = datetime.ctime(datetime.now())
  order_id = str(hash(json.dumps(data)))

  data['order_id'] = order_id 
  producer.publish(json.dumps({
    "event-type": "order-updated",
    "data": data
  }))
  db.access_tracking().insert_one({
    "order_id": order_id,
    "status": "PENDING"
  })
  return response_helper(200, {"order_id": order_id})

def response_helper(status, json_val=None, message=None):
  if (message == None):
    if (json_val == []):
      return jsonify({"msg": "Not Found"}), 404
    return jsonify(json_val), status
  else:
    return jsonify({"msg": message}), status

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5005, debug=True)