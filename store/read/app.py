from flask import Flask, abort, jsonify, request
from pymongo import MongoClient
import db

app = Flask(__name__)

# @app.route("/")
# def sample():
#   return "Store API service"

@app.route("/", methods=["GET"])
def get_all_stores():
  stores = db.access_stores()
  res = list(stores.find({}, {"_id": 0}))
  return response_helper(200, res)


@app.route("/<store_id>", methods=["GET"])
def get_one_store(store_id):
  stores = db.access_stores()
  res = list(stores.find({"store_id": store_id}, {"_id": 0}))
  return response_helper(200, res)


# @app.route("/<store_id>/status", methods=["GET"])
# def restaurant_status(store_id):
#   stores = access_stores()
#   res = list(stores.find(
#     {"store_id": store_id}, 
#     {"_id": 0, "restaurant_status": 1}
#   ))
#   res = [ dict(x).get("restaurant_status") for x in res ]
#   return response_helper(200, res)


# @app.route("/<store_id>/holiday-hours", methods=["GET"])
# def holiday_hours(store_id):
#   stores = access_stores()
#   old_val = list(stores.find(
#     {"store_id": store_id}, 
#     {"_id": 0, "holiday_hours": 1}
#   ))
#   return response_helper(200, old_val)

def response_helper(status, json_val, message=None):
  if (message == None):
    if (json_val == []):
      return jsonify({"msg": "Not Found"}), 404
    return jsonify(json_val), status
  else:
    return jsonify({"msg": message}), status

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5201, debug=True)