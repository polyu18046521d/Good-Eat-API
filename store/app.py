from flask import Flask, abort, jsonify, request
from pymongo import MongoClient
import sys

app = Flask(__name__)

# @app.route("/")
# def sample():
#   return "Store API service"

@app.route("/", methods=["GET"])
def get_all_stores():
  stores = access_stores()
  res = list(stores.find({}, {"_id": 0, "restaurant_status": 0, "holiday_hours": 0}))
  return response_helper(200, res)


@app.route("/<store_id>", methods=["GET"])
def get_one_store(store_id):
  stores = access_stores()
  res = list(stores.find({"store_id": store_id}, {"_id": 0, "restaurant_status": 0, "holiday_hours": 0}))
  return response_helper(200, res)


@app.route("/<store_id>/status", methods=["GET", "POST"])
def restaurant_status(store_id):
  stores = access_stores()
  if request.method == "POST":
    new_status = dict(request.get_json())["status"]
    res = stores.update_one(
      {"store_id": store_id},
      {"$set": {"restaurant_status.status": new_status}}
    )
    return response_helper(204, "")
  else:
    res = list(stores.find(
      {"store_id": store_id}, 
      {"_id": 0, "restaurant_status": 1}
    ))
    res = [ dict(x).get("restaurant_status") for x in res ]
    return response_helper(200, res)


@app.route("/<store_id>/holiday-hours", methods=["GET", "POST"])
def holiday_hours(store_id):
  stores = access_stores()
  old_val = list(stores.find(
    {"store_id": store_id}, 
    {"_id": 0, "holiday_hours": 1}
  ))
  if request.method == "POST":
    new_holidays_hours = dict(request.get_json())["holiday_hours"]
    new_val = dict(old_val[0])["holiday_hours"]
    for key, val in new_holidays_hours.items():
      new_val[key] = val
    stores.update_one(
      {"store_id": store_id},
      {"$set": {"holiday_hours": new_val}}
    )
    return response_helper(204, "")
  else:
    return response_helper(200, old_val)


def access_db():
  try:
    client = MongoClient(
        f"mongodb://{sys.argv[1]}:{sys.argv[2]}@{sys.argv[3]}:{sys.argv[4]}/"
    )  # connect with mongodb://username:password@host:port/
    return client["GoodEat"]
  except:
    abort(404, "Failed Database Connection")

def access_stores():
  return access_db()["stores"]

def response_helper(status, json_val, message=None):
  if (message == None):
    if (json_val == []):
      return jsonify({"msg": "Not Found"}), 404
    return jsonify(json_val), status
  else:
    return jsonify({"msg": message}), status

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5001, debug=True)