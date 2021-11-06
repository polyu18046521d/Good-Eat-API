import json
from flask import Flask, abort, jsonify, request
import db
import producer

from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

@app.route("/<store_id>", methods=["POST"])
def insert_new_menu(store_id):
  data = dict(request.get_json())
  menu = db.access_menu()
  res = menu.update_one({"store_id": store_id}, {"$push": {"menus": data}})
  producer.publish(json.dumps({
    "event-type": "menu-updated",
    "data": {
      "store_id": store_id,
      "menu": data
    }
  }))
  # return response_helper(200, res)
  return response_helper(204, "")

def response_helper(status, json_val, message=None):
  if (message == None):
    if (json_val == []):
      return jsonify({"msg": "Not Found"}), 404
    return jsonify(json_val), status
  else:
    return jsonify({"msg": message}), status

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5300)